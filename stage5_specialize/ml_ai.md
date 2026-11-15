# Track: Machine Learning & AI

**Stack:** NumPy · pandas · scikit-learn · PyTorch · Hugging Face · LLM APIs (Anthropic / OpenAI SDKs)
**Prerequisite:** the Data & Analytics track Milestones 1–2 (NumPy and pandas), or equivalent.

## Milestone 1: The math you need, in code
- **Learn:** vectors and matrices, dot products, derivatives and the chain rule, probability basics, mean and variance.
- **Build:** implement linear regression with gradient descent **in pure NumPy**.
- **Done when:** it matches `sklearn.linear_model.LinearRegression` to 3 decimal places and you can plot the loss curve.

## Milestone 2: Classical ML with scikit-learn
- **Learn:** train/validation/test splits, cross-validation, pipelines, preprocessing, the main model families (linear, tree ensembles, kNN), metrics (accuracy/precision/recall/F1/ROC-AUC, RMSE), overfitting, data leakage.
- **Build:** a tabular classifier on a real dataset (Titanic, Adult Income, or something from your own field).
- **Done when:** you use a `Pipeline` with no leakage, compare at least 3 models fairly with cross-validation, and write up error analysis on the misclassified examples.

## Milestone 3: Deep learning with PyTorch
- **Learn:** tensors, autograd, `nn.Module`, the training loop, DataLoaders, optimizers, GPU/MPS devices, regularization.
- **Build:** an MLP, then a small CNN on FashionMNIST, writing the training loop yourself.
- **Done when:** the CNN reaches at least 90% test accuracy, you log loss and accuracy curves, and you can explain every line of the training loop.

## Milestone 4: Transformers & Hugging Face
- **Learn:** tokenization, embeddings, attention (conceptually), pretrained models, fine-tuning, the `transformers` and `datasets` libraries.
- **Build:** fine-tune a small pretrained model for text classification.
- **Done when:** it beats a TF-IDF + logistic regression baseline that you also built.

## Milestone 5: Building with LLM APIs
- **Learn:** the messages API, system prompts, structured outputs, tool use / function calling, streaming, embeddings + retrieval (RAG), evaluation, cost and latency.
- **Build:** a RAG question-answering CLI over your own documents, with a tool the model can call.
- **Done when:** you have an eval set of at least 20 questions with expected answers, an automated score, and you can show that a change to the prompt or retrieval measurably improved it.

## Milestone 6: Shipping ML
- **Learn:** experiment tracking (MLflow or W&B), model serialization, serving behind FastAPI, monitoring drift.
- **Done when:** a model is served behind an HTTP endpoint with input validation and a test, and your experiments are reproducible from config.

## Capstone
Pick one:
- (a) An end-to-end ML project on data you collected yourself, with a deployed demo.
- (b) An LLM-powered application with tools, retrieval and an eval suite.

## Key reading
- *Hands-On Machine Learning*, 3rd ed. (Géron)
- fast.ai *Practical Deep Learning for Coders* (free)
- Andrej Karpathy's "Neural Networks: Zero to Hero" (free videos)
- *Deep Learning with PyTorch* (Stevens et al.)
