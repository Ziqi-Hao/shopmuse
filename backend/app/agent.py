"""
ShopMuse Agent: A unified commerce copilot that routes user intent
to the appropriate tool (catalog search, image search, or general chat).

Memory Architecture:
  - Layer 1 (Session): In-memory session state for multi-turn context
  - Layer 2 (Mem0): Persistent user preference memory across sessions
"""

import base64
import json
from openai import OpenAI

from app.models.schemas import ChatRequest, ChatResponse, Product
from app.tools.catalog_tools import (
    TOOL_SCHEMAS,
    catalog_text_search,
    get_product_by_id,
)
from app.memory import (
    get_session,
    add_to_session,
    get_session_context,
    add_to_long_term_memory,
    get_long_term_memories,
)

SYSTEM_PROMPT = """You are ShopMuse, a helpful and friendly AI shopping assistant. You help users discover and find products from our catalog.

Your capabilities:
1. **Product Recommendations**: When users describe what they're looking for, use the catalog_text_search tool to find matching products. Always search the catalog - never make up products.
2. **Product Lookup**: When users reference a specific product ID, use get_product_by_id to fetch details.
3. **General Conversation**: For greetings, general questions, or non-shopping queries, respond naturally without tools.

Guidelines:
- Always search the catalog when users ask about products. Never invent or hallucinate products.
- When recommending products, explain WHY each product matches what the user asked for.
- Be concise but helpful. Use a warm, conversational tone.
- If the user uploads an image, they want to find similar products in our catalog.
- If the user asks for cheaper/more expensive alternatives, adjust your search filters accordingly.
- You can suggest complementary items (e.g., "This jacket would pair well with...") but always back it up with a catalog search.
- Our catalog includes: t-shirts, shoes, bags, jackets, pants, and accessories.
- When presenting products, mention the product ID so users can reference it later.
- Pay attention to user preferences from memory context below. Use them to personalize recommendations.

Important: You MUST use the catalog_text_search tool for any product-related query. Do not answer product questions from memory."""


def detect_intent(message: str, has_image: bool) -> str:
    if has_image:
        return "image_search"
    shopping_keywords = [
        "recommend", "suggest", "find", "looking for", "show me", "want",
        "need", "buy", "shop", "search", "product", "item", "wear",
        "outfit", "clothes", "shirt", "shoes", "bag", "jacket", "pants",
        "cheaper", "expensive", "affordable", "budget", "style", "casual",
        "formal", "sporty", "similar", "like this", "alternative",
        "t-shirt", "sneakers", "boots", "backpack", "jeans", "dress",
        "accessories", "watch", "hat", "sunglasses", "belt", "wallet", "scarf",
    ]
    msg_lower = message.lower()
    if any(kw in msg_lower for kw in shopping_keywords):
        return "text_recommendation"
    return "general_chat"


class ShopMuseAgent:
    def __init__(self, api_key: str, base_url: str | None = None, model: str = "gpt-4o-mini"):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url or "https://api.openai.com/v1",
        )
        self.model = model

    async def process(self, request: ChatRequest) -> ChatResponse:
        has_image = request.image_base64 is not None and len(request.image_base64) > 0
        intent = detect_intent(request.message, has_image)

        # Use session_id if provided, otherwise generate one
        session_id = request.session_id or "default"
        user_id = session_id  # For Mem0, user_id maps to session_id

        # Handle image search directly
        if intent == "image_search":
            return await self._handle_image_search(request, session_id, user_id)

        # For text queries, use the LLM with tool calling
        return await self._handle_text_query(request, intent, session_id, user_id)

    def _build_system_prompt(self, session_id: str, user_id: str, query: str) -> str:
        """Build system prompt enriched with memory context."""
        prompt = SYSTEM_PROMPT

        # Layer 1: Session context
        session_ctx = get_session_context(session_id)
        if session_ctx:
            prompt += f"\n\n## Session Context\n{session_ctx}"

        # Layer 2: Long-term user preferences (Mem0) - never block on failure
        try:
            long_term_ctx = get_long_term_memories(user_id, query)
            if long_term_ctx:
                prompt += f"\n\n## User Memory\n{long_term_ctx}"
        except Exception:
            pass  # Memory is optional, never block the response

        return prompt

    async def _handle_image_search(self, request: ChatRequest, session_id: str, user_id: str) -> ChatResponse:
        # Step 1: Use LLM vision to describe the image
        describe_messages = [
            {"role": "system", "content": "You are a fashion product analyst. Describe the item in the image concisely: type (shirt, shoes, bag, etc.), color, style, material, and any distinctive features. Output only the description, no preamble."},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{request.image_base64}"},
                    },
                    {
                        "type": "text",
                        "text": request.message or "Describe this product image for searching similar items.",
                    },
                ],
            },
        ]

        description_response = self.client.chat.completions.create(
            model=self.model,
            messages=describe_messages,
            max_tokens=150,
        )
        image_description = description_response.choices[0].message.content

        # Step 2: Use the description to search catalog via text embeddings
        products = catalog_text_search(query=image_description, top_k=5)

        # Step 3: Generate explanation with the image + search results
        product_descriptions = "\n".join(
            f"- {p.title} ({p.id}): {p.description} [${p.price}]"
            for p in products
        )

        system_prompt = self._build_system_prompt(session_id, user_id, "image search")

        explain_messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{request.image_base64}"},
                    },
                    {
                        "type": "text",
                        "text": f"The user uploaded this image to find similar products. "
                        f"I analyzed the image as: {image_description}\n\n"
                        f"Here are matching products from our catalog:\n{product_descriptions}\n\n"
                        f"User message: {request.message or 'Find products similar to this image'}\n\n"
                        f"Explain how these products relate to the uploaded image. Be specific about visual similarities.",
                    },
                ],
            },
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=explain_messages,
            max_tokens=500,
        )

        reply = response.choices[0].message.content

        # Update memory
        add_to_session(session_id, "user", request.message or "[uploaded image]",
                       product_ids=[p.id for p in products])
        add_to_session(session_id, "assistant", reply)

        # Store in long-term memory
        add_to_long_term_memory(user_id, [
            {"role": "user", "content": request.message or "User searched by image"},
            {"role": "assistant", "content": reply},
        ])

        return ChatResponse(
            message=reply,
            products=products,
            intent="image_search",
        )

    async def _handle_text_query(self, request: ChatRequest, intent: str, session_id: str, user_id: str) -> ChatResponse:
        system_prompt = self._build_system_prompt(session_id, user_id, request.message)
        messages = [{"role": "system", "content": system_prompt}]

        # Use session history (server-side) + any client-provided history
        session = get_session(session_id)
        for msg in session["messages"][-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Also include client-side history if no session history exists
        if not session["messages"] and request.history:
            for msg in request.history[-10:]:
                if msg.role in ("user", "assistant"):
                    messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": request.message})

        # First call: let LLM decide whether to use tools
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            max_tokens=500,
        )

        assistant_message = response.choices[0].message
        all_products = []

        # Process tool calls if any
        if assistant_message.tool_calls:
            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                if func_name == "catalog_text_search":
                    products = catalog_text_search(**func_args)
                    all_products.extend(products)
                    tool_result = json.dumps([p.model_dump() for p in products])
                elif func_name == "get_product_by_id":
                    product = get_product_by_id(**func_args)
                    if product:
                        all_products.append(product)
                        tool_result = json.dumps(product.model_dump())
                    else:
                        tool_result = json.dumps({"error": "Product not found"})
                else:
                    tool_result = json.dumps({"error": f"Unknown tool: {func_name}"})

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                })

            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=600,
            )

            reply = final_response.choices[0].message.content
            product_ids = [p.id for p in all_products] if all_products else None

            # Update memory
            add_to_session(session_id, "user", request.message, product_ids=product_ids)
            add_to_session(session_id, "assistant", reply)

            # Store in long-term memory
            add_to_long_term_memory(user_id, [
                {"role": "user", "content": request.message},
                {"role": "assistant", "content": reply},
            ])

            return ChatResponse(
                message=reply,
                products=all_products if all_products else None,
                intent="text_recommendation",
            )

        # No tool calls = general chat
        reply = assistant_message.content

        # Update session memory
        add_to_session(session_id, "user", request.message)
        add_to_session(session_id, "assistant", reply)

        # Store in long-term memory
        add_to_long_term_memory(user_id, [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": reply},
        ])

        return ChatResponse(
            message=reply,
            products=None,
            intent="general_chat",
        )
