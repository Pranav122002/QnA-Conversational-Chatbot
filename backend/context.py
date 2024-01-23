def identify_context(question, dataset):
    question_keywords = set(question.lower().split())  # Convert question to lowercase and get keywords

    best_context = None
    highest_overlap = 0

    for context in dataset:
        context_lower = context.lower()
        context_keywords = set(context_lower.split())

        # Calculate the overlap between question keywords and context keywords
        overlap = len(question_keywords.intersection(context_keywords))

        # Update the best context if the overlap is higher
        if overlap > highest_overlap:
            best_context = context
            highest_overlap = overlap

    return best_context

# Example usage:
question = "What courses does FCRIT offer?"
dataset = [
    "Father Conceicao Rodrigues Institute of Technology (FCRIT) is a private engineering college.",
    "The institute offers the B.E degree courses in Computer Engineering, Electrical Engineering.",
]

best_context = identify_context(question, dataset)
print("Best context:", best_context)
