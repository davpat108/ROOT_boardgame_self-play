import torch
import torch.nn as nn

backbone_output_features = 64


class LinearNN_Backbone(nn.Module):
    def __init__(self, input_size):
        super(LinearNN_Backbone, self).__init__()
        self.hidden1 = nn.Linear(input_size, 128)
        self.hidden2 = nn.Linear(128, 64)
        self.output = nn.Linear(64, backbone_output_features)

        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x = self.relu(self.hidden1(x))
        x = self.dropout(x)
        x = self.relu(self.hidden2(x))
        x = self.output(x)
        return x


class LinearNN_Actor_Head(nn.Module):
    def __init__(self, output_features):
        super(LinearNN_Actor_Head, self).__init__()
        self.hidden1 = nn.Linear(backbone_output_features, 64)
        self.hidden2 = nn.Linear(64, 32)
        self.output = nn.Linear(32, output_features)

        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x = self.relu(self.hidden1(x))
        x = self.dropout(x)
        x = self.relu(self.hidden2(x))
        x = self.output(x)
        return x
    
class Compound_Linear_NN(nn.Module):
    def __init__(self, backbone, heads):
        super(Compound_Linear_NN, self).__init__()
        self.backbone = backbone
        self.heads = nn.ModuleList(heads)

    def forward(self, x, player_idx):
        shared_features = self.backbone(x)
        return self.heads[player_idx](shared_features)
    
def init_models_with_random_weights(cat_output_size, eyrie_output_size, alliance_output_size, vagabond_output_size, encoded_game_size):
    
    backbone = LinearNN_Backbone(encoded_game_size)
    cat_model = LinearNN_Actor_Head(cat_output_size)
    eyrie_model = LinearNN_Actor_Head(eyrie_output_size)
    alliance_model = LinearNN_Actor_Head(alliance_output_size)
    vagabond_model = LinearNN_Actor_Head(vagabond_output_size)
    
    return Compound_Linear_NN(backbone, [cat_model, eyrie_model, alliance_model, vagabond_model])
