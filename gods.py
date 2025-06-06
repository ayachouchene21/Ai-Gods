# -*- coding: utf-8 -*-
"""gods.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/gist/ayachouchene21/bcdeeeb147ec1da266a8d474c204ea95/gods.ipynb
"""

import pandas as pd

# Load dataset
train_df = pd.read_csv("/content/train.csv")
test_df = pd.read_csv("/content/test.csv")

# Display first few rows
print(train_df.head())

# Display basic information
print(train_df.info())  # Check data types and missing values
# Check the distribution of categories
print(train_df["target"].value_counts())  # Count of each category

# Fill missing titles with an empty string
train_df["title"].fillna("", inplace=True)

# Drop rows where content or target is missing
train_df.dropna(subset=["content", "target"], inplace=True)

print(train_df.head())

import re

def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r"http\S+", "", text)  # Remove URLs
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
    text = re.sub(r"\d+", "", text)  # Remove numbers
    return text
    train_df["content"] = train_df["content"].apply(clean_text)

# Fill missing values for title
train_df["title"] = train_df["title"].fillna("")

# Drop rows with missing content or target
train_df = train_df.dropna(subset=["content", "target"])

# Remove duplicates
train_df = train_df.drop_duplicates()

# Clean and standardize content column
train_df["content"] = train_df["content"].str.lower()

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download("stopwords")
nltk.download("punkt")

!pip install nltk
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download("stopwords")
nltk.download("punkt")
nltk.download('punkt_tab')
stop_words = set(stopwords.words("english"))

def tokenize_and_remove_stopwords(text):
    words = word_tokenize(text)  # Tokenize the text
    words = [word for word in words if word not in stop_words]  # Remove stopwords
    return " ".join(words)  # Reconstruct the sentence

train_df["content"] = train_df["content"].apply(tokenize_and_remove_stopwords)

from nltk.stem import WordNetLemmatizer

nltk.download("wordnet")
lemmatizer = WordNetLemmatizer()

def lemmatize_text(text):
    words = word_tokenize(text)
    words = [lemmatizer.lemmatize(word) for word in words]  # Lemmatize each word
    return " ".join(words)

train_df["content"] = train_df["content"].apply(lemmatize_text)

pip install transformers torch

from transformers import BertTokenizer, BertModel
import torch

# Load pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased')

def get_bert_embedding(text):
    # Tokenize the input text and convert to tensor
    tokens = tokenizer(text, padding='max_length', truncation=True, max_length=512, return_tensors="pt")

    # Get BERT embeddings
    with torch.no_grad():
        outputs = bert_model(**tokens)

    # Extract the CLS token's embedding (represents the entire sentence)
    cls_embedding = outputs.last_hidden_state[:, 0, :]

    return cls_embedding.numpy()  # Convert to NumPy array if needed

import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

bert_model.to(device)

def get_bert_embedding(text):
    tokens = tokenizer(text, padding='max_length', truncation=True, max_length=512, return_tensors="pt")
    tokens = {key: value.to(device) for key, value in tokens.items()}  # Move tokens to GPU

    with torch.no_grad():
        outputs = bert_model(**tokens)

    cls_embedding = outputs.last_hidden_state[:, 0, :]
    return cls_embedding.cpu().numpy()  # Move back to CPU before converting to NumPy

from torch.utils.data import DataLoader

def batch_bert_embedding(text_list, batch_size=32):
    dataloader = DataLoader(text_list, batch_size=batch_size)

    embeddings = []
    for batch in dataloader:
        tokens = tokenizer(batch, padding=True, truncation=True, max_length=512, return_tensors="pt")
        tokens = {key: value.to(device) for key, value in tokens.items()}  # Move to GPU

        with torch.no_grad():
            outputs = bert_model(**tokens)

        batch_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        embeddings.extend(batch_embeddings)

    return embeddings

train_df["bert_embedding"] = batch_bert_embedding(train_df["content"].tolist(), batch_size=32)

from transformers import DistilBertTokenizer, DistilBertModel

tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
bert_model = DistilBertModel.from_pretrained('distilbert-base-uncased').to(device)

import numpy as np
np.save("bert_embeddings.npy", train_df["bert_embedding"].values)

from sklearn.preprocessing import LabelEncoder

encoder = LabelEncoder()
train_df["target"] = encoder.fit_transform(train_df["target"])  # Convert labels to numbers

from sklearn.model_selection import train_test_split

X_train, X_val, y_train, y_val = train_test_split(
    train_df["content"], train_df["target"], test_size=0.2, random_state=42
)

# Show the first 5 rows of the dataset
print(train_df.head())