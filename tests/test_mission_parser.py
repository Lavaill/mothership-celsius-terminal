import pytest
from mothership.data.markdown_parser import MissionMarkdownParser

@pytest.fixture
def parser():
    return MissionMarkdownParser()

@pytest.fixture
def full_mission_markdown():
    return """---
id: AD-121
contract-title: Escort VIP
contract-pay: 1000cr
contract-hazard: 1
contract-client: Rossi N
mission-name: Operation Al Dente
---
# CONTRACT

### DESCRIPTION
VIP requires transport. Heavy equipment and potential industrial espionage to be expected.

### OBJECTIVES
- [ ] Deliver VIP | MDT
- [ ] Transport equipment | MDT

### PARAMETERS
- [ ] NDA {Non-Disclosure Agreement}
- [x] JUMPS {Mandatory}
- [ ] SALVAGE {}

### WARNINGS
- **DESC**: Free Pasta

# MISSION

### SUMMARY
Nonna Rossi is relocating her trattoria.

### LOCATION
- **NAME**: Transit Corridor G-4
- **REF**: Page 12

### CAST
- **NAME**: Nonna Rossi
- **TAGLINE**: Indomitable Matriarch
- **QUIRK**: Feeds anyone
- **WANT**: To keep the ravioli from overcooking.

- **NAME**: The Iron Press
- **TAGLINE**: 2-Ton Antique Machine
- **QUIRK**: BIFL
- **WANT**: To drift blindly.

### SCENES
- **DESC**: The gravity plating fails.

### REWARDS
- **TYPE**: Contact
- **DESC**: Nonna Rossi. Infinite Pasta
"""

def test_parse_metadata(parser, full_mission_markdown):
    result = parser.parse(full_mission_markdown)
    assert result["id"] == "AD-121"
    assert len(result["entries"]) == 2

def test_parse_contract(parser, full_mission_markdown):
    result = parser.parse(full_mission_markdown)
    contract = next(e["data"] for e in result["entries"] if e["type"] == "contract")
    
    assert contract["client"] == "Rossi N"
    assert contract["missionName"] == "Escort VIP"
    assert contract["missionPay"]["text"] == "1000"
    assert contract["missionPay"]["unit"] == "cr"
    assert contract["hazard"] == 1
    assert "VIP requires transport" in contract["missionDescription"]
    
    # Objectives
    assert len(contract["objectives"]) == 2
    assert contract["objectives"][0]["objective"] == "Deliver VIP"
    assert contract["objectives"][0]["pay"] == "MDT"
    
    # Parameters
    assert len(contract["params"]) == 3
    assert contract["params"][0]["name"] == "NDA"
    assert contract["params"][0]["info"] == "Non-Disclosure Agreement"
    assert contract["params"][0]["checkbox"] == "[ ]"
    assert contract["params"][1]["checkbox"] == "[x]"
    
    # Warnings
    assert len(contract["warnings"]) == 1
    assert contract["warnings"][0]["text"] == "Free Pasta"

def test_parse_mission(parser, full_mission_markdown):
    result = parser.parse(full_mission_markdown)
    mission = next(e["data"] for e in result["entries"] if e["type"] == "mission")
    
    assert mission["title"] == "Operation Al Dente"
    assert "Nonna Rossi is relocating" in mission["summary"]
    assert mission["location"] == "Transit Corridor G-4"
    assert mission["locationRef"] == "Page 12"
    
    # Cast
    assert len(mission["cast"]) == 2
    assert mission["cast"][0]["name"] == "Nonna Rossi"
    assert mission["cast"][0]["tagline"] == "Indomitable Matriarch"
    assert mission["cast"][1]["name"] == "The Iron Press"
    
    # Scenes
    assert len(mission["scenes"]) == 1
    assert mission["scenes"][0]["desc"] == "The gravity plating fails."
    
    # Rewards
    assert len(mission["rewards"]) == 1
    assert mission["rewards"][0]["type"] == "Contact"
    assert mission["rewards"][0]["desc"] == "Nonna Rossi. Infinite Pasta"

def test_empty_sections(parser):
    content = """---
id: EMPTY
---
# CONTRACT
# MISSION
"""
    result = parser.parse(content)
    assert result["id"] == "EMPTY"
    contract = result["entries"][0]["data"]
    assert contract["objectives"] == []
    assert contract["params"] == []
