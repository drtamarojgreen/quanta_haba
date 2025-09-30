class PromptPacker:
    """
    Packs a conversation into a single prompt string formatted for Llama 3.1.
    """

    SPECIAL_TOKENS = {
        "begin_of_text": "<|begin_of_text|>",
        "end_of_text": "<|end_of_text|>",
        "start_header": "<|start_header_id|>",
        "end_header": "<|end_header_id|>",
        "end_of_message": "<|eom_id|>",
        "end_of_turn": "<|eot_id|>",
        "python_tag": "<|python_tag|>"
    }

    SUPPORTED_ROLES = ["system", "user", "assistant", "ipython"]

    def pack_message(self, role, content, end_of_turn=True):
        """Packs a single message."""
        if role not in self.SUPPORTED_ROLES:
            raise ValueError(f"Unsupported role: {role}")

        packed_message = (
            f"{self.SPECIAL_TOKENS['start_header']}{role}{self.SPECIAL_TOKENS['end_header']}\\n"
            f"\\n"
            f"{content}"
        )

        if end_of_turn:
            packed_message += self.SPECIAL_TOKENS['end_of_turn']
        else:
            packed_message += self.SPECIAL_TOKENS['end_of_message']

        return packed_message

    def pack_conversation(self, messages):
        """
        Packs a list of messages into a single prompt string.

        Args:
            messages (list): A list of dictionaries, where each dictionary
                             has a "role" and "content" key.

        Returns:
            str: The packed prompt string.
        """
        prompt_str = self.SPECIAL_TOKENS['begin_of_text']

        for i, msg in enumerate(messages):
            role = msg.get("role")
            content = msg.get("content")

            is_eot = True
            if role == "ipython":
                 is_eot = True

            if role == "assistant" and "tool_calls" in content:
                is_eot = False

            prompt_str += self.pack_message(role, content, end_of_turn=is_eot)

        if messages and messages[-1]['role'] != 'assistant':
             prompt_str += f"{self.SPECIAL_TOKENS['start_header']}assistant{self.SPECIAL_TOKENS['end_header']}\\n\\n"

        return prompt_str