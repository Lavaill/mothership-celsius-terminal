import re
import yaml
import json
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from mothership.core.utils import logger
from mothership.core.config import CACHE_PATH

class MarkdownParser(ABC):
    """Base class for all Markdown-based data parsers."""
    
    @abstractmethod
    def parse(self, content: str) -> Dict[str, Any]:
        """Parses the given Markdown content into a structured dictionary."""
        pass

    def extract_yaml_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Extracts YAML frontmatter from the start of the Markdown content."""
        match = re.match(r'^---\s*\n(.*?)\n---(?:\s*\n|$)(.*)', content, re.DOTALL)
        if match:
            yaml_str, markdown_body = match.groups()
            try:
                # Use a safe loader for YAML
                frontmatter = yaml.safe_load(yaml_str) or {}
                return frontmatter, markdown_body
            except yaml.YAMLError:
                return {}, content
        return {}, content

    def _validate_and_log(self, data: Any, path: str = "") -> None:
        """Recursively checks for empty fields and logs warnings for critical fields."""
        # List of fields that are OK to be empty or optional
        OPTIONAL_FIELDS = {"info", "quirk", "want", "tagline", "locationRef", "warnings", "rewards", "scenes", "params"}
        
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                if value in (None, "", [], {}):
                    if key not in OPTIONAL_FIELDS:
                        logger.warning(f"Empty field detected during parsing: '{new_path}'")
                else:
                    self._validate_and_log(value, new_path)
        elif isinstance(data, list):
            if not data:
                # Only warn for empty lists if they aren't in the optional set
                field_name = path.split('.')[-1] if '.' in path else path
                if field_name not in OPTIONAL_FIELDS:
                    logger.warning(f"Empty list detected during parsing: '{path}'")
            for i, item in enumerate(data):
                self._validate_and_log(item, f"{path}[{i}]")

    def _cache_result(self, data: Dict[str, Any]) -> None:
        """Stores the full JSON output temporarily in the vault_cache folder."""
        try:
            os.makedirs(CACHE_PATH, exist_ok=True)
            # Use mission ID for filename
            mission_id = data.get("id", "UNKNOWN").replace("/", "_").replace("\\", "_")
            cache_file = os.path.join(CACHE_PATH, f"{mission_id}.json")
            
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Cached parsed mission to: {cache_file}")
        except Exception as e:
            logger.error(f"Failed to cache parsing result: {e}")

class MissionMarkdownParser(MarkdownParser):
    """Parser for Mothership Mission and Contract Markdown templates."""

    def parse(self, content: str) -> Dict[str, Any]:
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        frontmatter, body = self.extract_yaml_frontmatter(content)
        
        # Split body into sections by # Headers
        sections = self._split_sections(body)
        
        contract_section = sections.get("CONTRACT", "")
        mission_section = sections.get("MISSION", "")
        
        # Parse Contract Data
        contract_data = self._parse_contract(contract_section, frontmatter)
        
        # Parse Mission Data
        mission_data = self._parse_mission(mission_section, frontmatter)
        
        result = {
            "id": frontmatter.get("id", "UNKNOWN"),
            "entries": [
                {"type": "contract", "data": contract_data},
                {"type": "mission", "data": mission_data}
            ]
        }
        
        # Upgrade: Validate and Cache
        self._validate_and_log(result)
        self._cache_result(result)
        
        return result

    def _split_sections(self, body: str) -> Dict[str, str]:
        """Splits the markdown body into top-level # sections."""
        sections = {}
        # Find all # HEADERS
        matches = list(re.finditer(r'^\s*#\s+([A-Z]+)\b', body, re.MULTILINE | re.IGNORECASE))
        
        for i, match in enumerate(matches):
            section_name = match.group(1).upper()
            start = match.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(body)
            sections[section_name] = body[start:end].strip()
            
        return sections

    def _parse_contract(self, section: str, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        # Sub-sections use ###
        sub_sections = self._split_sub_sections(section)
        
        # Objectives: - [ ] {OBJECTIVE} | {PAY_DETAIL}
        objectives = []
        obj_text = sub_sections.get("OBJECTIVES", "")
        for line in obj_text.split('\n'):
            match = re.match(r'^- \[[ xX]\]\s*(.*?)\s*\|\s*(.*)', line.strip())
            if match:
                objectives.append({
                    "objective": match.group(1).strip(),
                    "pay": match.group(2).strip()
                })

        # Parameters: - [ ] {NAME}  {{INFO}}
        params = []
        params_text = sub_sections.get("PARAMETERS", "")
        for line in params_text.split('\n'):
            match = re.match(r'^- (\[[ xX]\])\s*(.*?)\s*\{(.*?)\}', line.strip())
            if match:
                params.append({
                    "checkbox": match.group(1),
                    "name": match.group(2).strip(),
                    "info": match.group(3).strip()
                })
            elif line.strip().startswith("-"):
                 # Basic check for parameters without info braces
                 match = re.match(r'^- (\[[ xX]\])\s*(.*)', line.strip())
                 if match:
                    params.append({
                        "checkbox": match.group(1),
                        "name": match.group(2).strip(),
                        "info": ""
                    })

        # Warnings: - **DESC**: {TEXT}
        warnings = []
        warnings_text = sub_sections.get("WARNINGS", "")
        for line in warnings_text.split('\n'):
            match = re.match(r'^- \*\*DESC\*\*:\s*(.*)', line.strip())
            if match:
                warnings.append({"text": match.group(1).strip()})

        # Mission Pay parsing
        pay_raw = str(frontmatter.get("contract-pay", "0"))
        # Try to extract number and unit
        pay_match = re.match(r'(\d+)\s*(.*)', pay_raw)
        if pay_match:
            pay_text, pay_unit = pay_match.groups()
        else:
            pay_text, pay_unit = pay_raw, "cr"

        return {
            "client": frontmatter.get("contract-client", "UNKNOWN"),
            "missionDescription": sub_sections.get("DESCRIPTION", "").strip(),
            "id": frontmatter.get("id", "UNKNOWN"),
            "missionName": frontmatter.get("contract-title", "UNKNOWN"),
            "missionPay": {
                "text": pay_text,
                "unit": pay_unit or "cr"
            },
            "hazard": frontmatter.get("contract-hazard", 1),
            "objectives": objectives,
            "params": params,
            "warnings": warnings
        }

    def _parse_mission(self, section: str, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        sub_sections = self._split_sub_sections(section)
        
        # Location
        loc_text = sub_sections.get("LOCATION", "")
        loc_name = ""
        loc_ref = ""
        # Use re.MULTILINE explicitly or remove ^ if not at start of string
        name_match = re.search(r'^\s*-\s*\*\*NAME\*\*:\s*(.*)', loc_text, re.MULTILINE)
        if name_match: loc_name = name_match.group(1).strip()
        ref_match = re.search(r'^\s*-\s*\*\*REF\*\*:\s*(.*)', loc_text, re.MULTILINE)
        if ref_match: loc_ref = ref_match.group(1).strip()

        # Cast (multiple blocks)
        cast = []
        cast_text = sub_sections.get("CAST", "")
        # Split by empty lines or start of new - **NAME**
        cast_blocks = re.split(r'\n\s*(?=-\s*\*\*NAME\*\*:)', cast_text)
        for block in cast_blocks:
            if not block.strip(): continue
            name = re.search(r'-\s*\*\*NAME\*\*:\s*(.*)', block)
            tagline = re.search(r'-\s*\*\*TAGLINE\*\*:\s*(.*)', block)
            quirk = re.search(r'-\s*\*\*QUIRK\*\*:\s*(.*)', block)
            want = re.search(r'-\s*\*\*WANT\*\*:\s*(.*)', block)
            if name:
                cast.append({
                    "name": name.group(1).strip(),
                    "tagline": tagline.group(1).strip() if tagline else "",
                    "quirk": quirk.group(1).strip() if quirk else "",
                    "want": want.group(1).strip() if want else ""
                })

        # Scenes
        scenes = []
        scenes_text = sub_sections.get("SCENES", "")
        for line in scenes_text.split('\n'):
            match = re.search(r'^\s*-\s*\*\*DESC\*\*:\s*(.*)', line)
            if match:
                scenes.append({"desc": match.group(1).strip()})

        # Rewards
        rewards = []
        rewards_text = sub_sections.get("REWARDS", "")
        reward_blocks = re.split(r'\n\s*(?=-\s*\*\*TYPE\*\*:)', rewards_text)
        for block in reward_blocks:
            if not block.strip(): continue
            r_type = re.search(r'-\s*\*\*TYPE\*\?:\s*(.*)', block)
            if not r_type:
                 r_type = re.search(r'-\s*\*\*TYPE\*\*:\s*(.*)', block)
            r_desc = re.search(r'-\s*\*\*DESC\*\*:\s*(.*)', block)
            if r_type and r_desc:
                rewards.append({
                    "type": r_type.group(1).strip(),
                    "desc": r_desc.group(1).strip()
                })

        return {
            "id": frontmatter.get("id", "UNKNOWN"),
            "title": frontmatter.get("mission-name", "UNKNOWN"),
            "summary": sub_sections.get("SUMMARY", "").strip(),
            "location": loc_name,
            "locationRef": loc_ref,
            "cast": cast,
            "scenes": scenes,
            "rewards": rewards
        }

    def _split_sub_sections(self, section_text: str) -> Dict[str, str]:
        """Splits a section into ### sub-sections."""
        subs = {}
        matches = list(re.finditer(r'^\s*###\s+([A-Z\s]+)(?:\n|$)', section_text, re.MULTILINE | re.IGNORECASE))
        for i, match in enumerate(matches):
            sub_name = match.group(1).strip().upper()
            start = match.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(section_text)
            subs[sub_name] = section_text[start:end].strip()
        return subs
