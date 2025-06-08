import os

# Set test environment variables
os.environ["LANGCHAIN_API_KEY"] = "test_langsmith_key"
os.environ["PINECONE_API_KEY"] = "test_pinecone_key"
os.environ["AWS_ACCESS_KEY_ID"] = "test_aws_key"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test_aws_secret"
os.environ["ANTHROPIC_API_KEY"] = "test_anthropic_key"

# Verify environment variables are set
print("\nEnvironment variables set:")
print("-" * 50)
for key in ["LANGCHAIN_API_KEY", "PINECONE_API_KEY", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "ANTHROPIC_API_KEY"]:
    print(f"{key}: {os.environ.get(key)}")
print("-" * 50)

# Verify Pinecone environment
print("\nPinecone environment setup:")
print("-" * 50)
print(f"Pinecone API Key: {os.environ.get('PINECONE_API_KEY')}")
print("-" * 50)

# Verify AWS environment
print("\nAWS environment setup:")
print("-" * 50)
print(f"AWS Access Key: {os.environ.get('AWS_ACCESS_KEY_ID')}")
print(f"AWS Secret Key: {os.environ.get('AWS_SECRET_ACCESS_KEY')}")
print("-" * 50)

# Verify Anthropic environment
print("\nAnthropic environment setup:")
print("-" * 50)
print(f"Anthropic API Key: {os.environ.get('ANTHROPIC_API_KEY')}")
print("-" * 50)
