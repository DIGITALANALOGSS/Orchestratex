class MentorAgent:
    async def teach(self, user_profile, user_input, result):
        """Provide explanations, encouragement, and next-step suggestions."""
        explanation = self.explain(result)
        encouragement = self.encourage(user_profile)
        next_steps = self.suggest_next(user_profile, result)
        print(f"\nMentor: {explanation}\n{encouragement}\nNext: {next_steps}")

    def explain(self, result):
        """Use LLM for natural language explanation."""
        return f"Here's how I solved your task: {result}"

    def encourage(self, user_profile):
        """Provide personalized encouragement."""
        return "You're making great progress! Keep exploring."

    def suggest_next(self, user_profile, result):
        """Suggest new skills or workflows based on learning graph."""
        return "Would you like to try automating another task or learn more about this topic?"
