# media/directory_analyzer.py
import os
from collections import Counter
from typing import Dict, List, Tuple, Set
import re

class DirectoryAnalyzer:
    def __init__(self):
        self.supported_audio_formats: Set[str] = {'.mp3', '.m4a', '.wav', '.flac', '.aac'}
        self.year_pattern = re.compile(r'^\d{4}$')
        
    def analyze_directory(self, root_path: str) -> str:
        """Analyze music directory structure and determine organization hierarchy."""
        if not os.path.exists(root_path):
            raise ValueError(f"Directory {root_path} does not exist")

        # Get directory structure information
        structure_info = self._scan_directory(root_path)
        depth_stats = self._analyze_depth(structure_info)
        year_locations = self._find_year_tiers(structure_info)
        
        return self._determine_hierarchy(depth_stats, year_locations)

    def _scan_directory(self, root_path: str) -> List[Dict[str, any]]:
        """Scan directory and collect structure information."""
        structures = []
        
        for root, dirs, files in os.walk(root_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            # Only process paths that lead to music files
            has_music = any(f.lower().endswith(tuple(self.supported_audio_formats)) for f in files)
            if has_music:
                rel_path = os.path.relpath(root, root_path)
                if rel_path != '.':
                    path_parts = rel_path.split(os.sep)
                    structures.append({
                        'depth': len(path_parts),
                        'parts': path_parts
                    })
        
        return structures

    def _analyze_depth(self, structures: List[Dict[str, any]]) -> Dict[str, any]:
        """Analyze the depth statistics of the directory structure."""
        depths = Counter(s['depth'] for s in structures)
        total = sum(depths.values())
        
        depth_stats = {
            'max_depth': max(depths.keys()) if depths else 0,
            'common_depth': depths.most_common(1)[0][0] if depths else 0,
            'depth_distribution': {d: count/total for d, count in depths.items()} if total > 0 else {}
        }
        
        return depth_stats

    def _find_year_tiers(self, structures: List[Dict[str, any]]) -> Dict[int, float]:
        """Identify tiers that contain years and their consistency."""
        year_counts: Dict[int, Dict[str, int]] = {}
        
        for structure in structures:
            for i, part in enumerate(structure['parts']):
                if self.year_pattern.match(part):
                    if i not in year_counts:
                        year_counts[i] = {'total': 0, 'year_count': 0}
                    year_counts[i]['total'] += 1
                    year_counts[i]['year_count'] += 1
        
        # Calculate percentage of year occurrence in each tier
        year_percentages = {}
        for tier, counts in year_counts.items():
            if counts['total'] > 0:
                percentage = counts['year_count'] / counts['total']
                if percentage > 0.9:  # 90% threshold
                    year_percentages[tier] = percentage
        
        return year_percentages

    def _determine_hierarchy(self, depth_stats: Dict[str, any], year_locations: Dict[int, float]) -> str:
        """Determine the most likely hierarchy based on analysis."""
        max_depth = depth_stats['max_depth']
        common_depth = depth_stats['common_depth']
        
        # Convert depth to hierarchy
        if max_depth == 2:
            return "Artist > Album > Song"
        
        if max_depth == 3:
            if year_locations:
                year_tier = list(year_locations.keys())[0]
                if year_tier == 0:
                    return "Year > Artist > Album > Song"
                elif year_tier == 1:
                    return "Artist > Year > Album > Song"
                else:
                    return "Artist > Album > Year > Song"
            return "Genre > Artist > Album > Song"
        
        if max_depth == 4:
            if year_locations:
                year_tier = list(year_locations.keys())[0]
                if year_tier == 1:
                    return "Genre > Year > Artist > Album > Song"
                elif year_tier == 2:
                    return "Genre > Artist > Year > Album > Song"
                else:
                    return "Genre > Artist > Album > Year > Song"
            return "Genre > Artist > Album > Song"
        
        # Default fallback
        return "Artist > Album > Song"

    def get_hierarchy_options(self, root_path: str) -> List[str]:
        """Get all valid hierarchy options based on directory structure."""
        try:
            base_hierarchy = self.analyze_directory(root_path)
            # Always include some basic options
            options = [
                base_hierarchy,
                "Artist > Album > Song",
                "Album > Song",
                "Song"
            ]
            return list(dict.fromkeys(options))  # Remove duplicates while preserving order
        except Exception as e:
            print(f"Error analyzing directory: {str(e)}")
            return [
                "Artist > Album > Song",
                "Album > Song",
                "Song"
            ]