import json
import os
import random

class QLearningAI:
    def __init__(self, n, storage_file='ai_memory.json'):
        self.n = n
        self.storage_file = storage_file
        self.q_table = self._load_q_table()
        self.alpha = 0.5  # learning rate
        self.gamma = 0.9  # discount factor
        self.epsilon = 0.1  # exploration rate

    def _load_q_table(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        return {}

    def save_q_table(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.q_table, f)

    def get_action(self, state):
        # Epsilon-greedy: explore or exploit
        if state not in self.q_table or random.random() < self.epsilon:
            # Explore: random action
            return None
        # Exploit: best known action
        actions = self.q_table[state]
        best_col = max(actions, key=actions.get)
        return int(best_col)

    def update(self, state, action, reward, next_state):
        state = str(state)
        action = str(action)
        if state not in self.q_table:
            self.q_table[state] = {}
        if action not in self.q_table[state]:
            self.q_table[state][action] = 0
        # Q-learning update
        next_max = 0
        if next_state in self.q_table and self.q_table[next_state]:
            next_max = max(self.q_table[next_state].values())
        self.q_table[state][action] += self.alpha * (reward + self.gamma * next_max - self.q_table[state][action]) 