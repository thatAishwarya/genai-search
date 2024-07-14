# Document Search and Summarization Application

## Overview

This application allows users to input queries and search through a folder of compliance PDF documents. Using BERT and Sentence Transformers, it retrieves relevant sections from the documents and provides a summary, including the document name and page number.

## Features

- Search for specific terms or questions within a set of PDF documents.
- Retrieve relevant document sections with a summary.
- Display document name and page number for easy reference.

## Requirements

To run this application, you will need the following Python packages:

- `torch`
- `torchvision`
- `torchaudio`
- `sentence-transformers`
- `transformers`
- `faiss-cpu`
- `PyMuPDF`

You can install the required packages using pip:

```bash
pip install torch torchvision torchaudio sentence-transformers transformers faiss-cpu PyMuPDF
