import torch
import torch.nn as nn
import numpy as np
import os

class CharacterCNN(nn.Module):
    def __init__(self, num_classes=36): # 26 letters + 10 digits
        super(CharacterCNN, self).__init__()
        # Simple LeNet-style architecture for 28x28 images
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(-1, 64 * 7 * 7)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

class CharacterRecognizer:
    def __init__(self, model_path='models/char_cnn.pth'):
        self.model_path = model_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.model = CharacterCNN()
        if os.path.exists(self.model_path):
            self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        
        # Character mapping: 0-9, A-Z
        self.class_mapping = {i: str(i) for i in range(10)}
        self.class_mapping.update({i+10: chr(i+65) for i in range(26)})

    def predict_characters(self, char_images):
        """
        Takes a list of 28x28 numpy arrays and returns the predicted string.
        """
        if not char_images:
            return ""
            
        result = ""
        with torch.no_grad():
            for img in char_images:
                # Convert to tensor: shape (1, 1, 28, 28)
                img_tensor = torch.tensor(img, dtype=torch.float32).unsqueeze(0).unsqueeze(0) / 255.0
                img_tensor = img_tensor.to(self.device)
                
                outputs = self.model(img_tensor)
                _, predicted = torch.max(outputs, 1)
                
                char_idx = predicted.item()
                result += self.class_mapping.get(char_idx, "?")
                
        return result

if __name__ == "__main__":
    pass
