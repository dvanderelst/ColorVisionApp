import random


def sample_colors(total_colors, target_color):
    distractor_colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan']
    distractor_colors.remove(target_color)
    random.shuffle(distractor_colors)
    number_targets = random.choice([1, 2, 3])
    selected_colors = [target_color] * number_targets
    for distractor_color in distractor_colors:
        number_distractors = random.choice([1, 2, 3])
        distractors = [distractor_color] * number_distractors
        selected_colors.extend(distractors)
    while len(selected_colors) < total_colors:
        selected_colors.append(random.choice(distractor_colors))
    selected_colors = selected_colors[:total_colors]
    random.shuffle(selected_colors)
    return selected_colors
