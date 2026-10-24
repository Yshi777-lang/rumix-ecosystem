#!/data/data/com.termux/files/usr/bin/bash
# test_07 — Provider: LocalProvider + MockProvider (подмена)

cd "$HOME/rumix/agents" || exit 1

python3 -c "
import sys
sys.path.insert(0, '.')
from runtime.provider import ModelProvider, ModelRequest, ModelResponse
from runtime.local_provider import LocalProvider

# TEST 01: LocalProvider существует и имеет generate
if not hasattr(LocalProvider, 'generate'):
    print('FAIL: LocalProvider без generate')
    sys.exit(1)

# TEST 02: LocalProvider — наследник ModelProvider
if not issubclass(LocalProvider, ModelProvider):
    print('FAIL: LocalProvider не наследник ModelProvider')
    sys.exit(1)

# TEST 03: MockProvider подменяет LocalProvider
class MockProvider(ModelProvider):
    name = 'mock'
    model = 'test'
    def generate(self, request):
        return ModelResponse(text='TEST', provider=self.name, model=self.model)

p = MockProvider()
req = ModelRequest(messages=[{'role': 'user', 'content': 'hi'}])
resp = p.generate(req)

if resp.text != 'TEST':
    print('FAIL: MockProvider не вернул TEST')
    sys.exit(1)

if resp.provider != 'mock':
    print('FAIL: provider != mock')
    sys.exit(1)

print('OK: Provider работает. MockProvider подменяет.')
sys.exit(0)
"
