import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split
from pathlib import Path

# Add the parent directory to sys.path so we can import src.recognition.CharacterCNN
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.recognition import CharacterCNN

def main():
    base_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    data_dir = base_dir / "data" / "characters"
    models_dir = base_dir / "models"
    
    if not data_dir.exists():
        print(f"Error: {data_dir} not found. Please run generate_char_data.py first.")
        return
        
    models_dir.mkdir(exist_ok=True)
    
    # Define transformations for the dataset
    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.Resize((28, 28)),
        transforms.ToTensor()
    ])
    
    # Load dataset
    print(f"Loading dataset from {data_dir}...")
    dataset = datasets.ImageFolder(root=str(data_dir), transform=transform)
    
    # Ensure we got 36 classes
    num_classes = len(dataset.classes)
    print(f"Found {len(dataset)} images across {num_classes} classes.")
    if num_classes != 36:
        print(f"Warning: Expected 36 classes (0-9, A-Z), but found {num_classes}.")
        
    # Split into train/val
    val_size = int(0.15 * len(dataset))
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, num_workers=0)
    
    # Initialize Model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    model = CharacterCNN(num_classes=num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    epochs = 10
    best_val_loss = float('inf')
    best_model_path = models_dir / "char_cnn.pth"
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for i, (inputs, labels) in enumerate(train_loader):
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
        train_acc = 100 * correct / total
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
                
        val_acc = 100 * val_correct / val_total
        val_loss /= len(val_loader)
        
        print(f"Epoch [{epoch+1}/{epochs}] - Loss: {running_loss/len(train_loader):.4f}, "
              f"Acc: {train_acc:.2f}% | Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
              
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            print("  --> Saving model...")
            torch.save(model.state_dict(), str(best_model_path))
            
    print("Training finished!")
    print(f"Best model saved to {best_model_path}")

if __name__ == "__main__":
    main()
