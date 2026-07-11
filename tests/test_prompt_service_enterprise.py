from services.prompt_service import PromptService

service = PromptService()

print("=" * 60)
print("Statistics")
print("=" * 60)

print(service.get_statistics())

print()

print("=" * 60)
print("Categories")
print("=" * 60)

print(service.get_categories())

print()

print("=" * 60)
print("Recent")
print("=" * 60)

for p in service.recent():
    print(dict(p))

print()

print("=" * 60)
print("Most Used")
print("=" * 60)

for p in service.most_used():
    print(dict(p))
