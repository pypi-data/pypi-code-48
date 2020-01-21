import torch
import torch.nn as nn
import torch.nn.functional as F


def expand_visits(sequence):
    flattened, offsets = [], []
    for idx, visit in enumerate(sequence):
        flattened.extend(visit)
        offsets.append(idx)
    flattened = torch.tensor(flattened).long()
    offsets = torch.tensor(offsets).long()
    return flattened, offsets


class ClinicalEmbedding(nn.Module):
    def __init__(self, num_concepts, emb_sz, max_visits=50, max_norm=1, mode='sum'):
        super().__init__()
        self.embedding = nn.EmbeddingBag(num_concepts, emb_sz, max_norm=max_norm, mode=mode)
        self.max_visits = max_visits

    def forward(self, x):
        """Convert the medical history, i.e. diagnnosis, medications into embeddings

        Input is a Python list of length equals the batch size.
        Each element within the list represents the medical history for an individual,
        and each element itself is a list of list, where the length of the outer list
        equals the number of the visits and the length of the inner list equals the number
        of the medical codes during that visit.
        """
        batch_max_visits = max(len(visit) for visit in x)
        if batch_max_visits > self.max_visits:
            batch_max_visits = self.max_visits
        embeds = []
        for seq in x:
            embed = self.embedding(*expand_visits(seq))
            embed = F.pad(embed, [0, 0, batch_max_visits - len(seq), 0])
            embeds.append(embed)
        return torch.stack(embeds)
