import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix the two broken border template literals in the HQ filter section
c = c.replace(
    "          border: ,\n          fontFamily: SoS.sans, fontSize: 11, fontWeight: hqFilter === 'alle' ? 700 : 400,\n          cursor: 'pointer' }}>Alle HQ</button>",
    "          border: `1px solid ${hqFilter === 'alle' ? SoS.ink : SoS.line}`,\n          fontFamily: SoS.sans, fontSize: 11, fontWeight: hqFilter === 'alle' ? 700 : 400,\n          cursor: 'pointer' }}>Alle HQ</button>",
    1
)

c = c.replace(
    "            border: ,\n            fontFamily: SoS.sans, fontSize: 11, fontWeight: hqFilter === hq ? 700 : 400,\n            cursor: 'pointer' }}>{hq}</button>",
    "            border: `1px solid ${hqFilter === hq ? SoS.ink : SoS.line}`,\n            fontFamily: SoS.sans, fontSize: 11, fontWeight: hqFilter === hq ? 700 : 400,\n            cursor: 'pointer' }}>{hq}</button>",
    1
)

with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('D template literals fixed')
