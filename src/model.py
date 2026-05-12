import torch
import torch.nn as nn


class SentimentANN(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim):
        super(SentimentANN, self).__init__()

        self.embedding = nn.Embedding(vocab_size, embed_dim)

        self.layers = nn.Sequential(
            nn.Linear(embed_dim,hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.6),

            nn.Linear(hidden_dim, 32),
            nn.ReLU(),

            nn.Linear(32,1),
            nn.Sigmoid()
        )

    def forward(self, x: torch.tensor) -> torch.tensor:
        x = self.embedding(x)
        x = torch.mean(x, dim=1)
        x = self.layers(x)
        return x