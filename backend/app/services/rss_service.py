"""RSS feed aggregator for travel deal sites"""
import feedparser
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlparse

from config.settings import settings


class RSSService:
    """Service for fetching and parsing RSS feeds from travel deal sites"""

    def __init__(self):
        self.feeds = self._get_feed_urls()

    def _get_feed_urls(self) -> List[Dict[str, str]]:
        """Get RSS feed URLs from settings"""
        return settings.TRAVEL_DEAL_SITES

    def fetch_feed(self, feed_url: str) -> List[Dict]:
        """
        Fetch and parse a single RSS feed

        Args:
            feed_url: URL of the RSS feed

        Returns:
            List of parsed feed entries
        """
        try:
            feed = feedparser.parse(feed_url)

            entries = []
            for entry in feed.entries:
                parsed_entry = self._parse_entry(entry, feed_url)
                if parsed_entry:
                    entries.append(parsed_entry)

            return entries

        except Exception as e:
            print(f"Error fetching feed {feed_url}: {e}")
            return []

    def fetch_all_feeds(self) -> List[Dict]:
        """
        Fetch all configured RSS feeds

        Returns:
            List of all parsed entries from all feeds
        """
        all_entries = []

        for feed_info in self.feeds:
            feed_url = feed_info['url']
            source_name = feed_info['name']

            entries = self.fetch_feed(feed_url)

            # Add source name to each entry
            for entry in entries:
                entry['source_name'] = source_name

            all_entries.extend(entries)

        return all_entries

    def _parse_entry(self, entry, feed_url: str) -> Optional[Dict]:
        """
        Parse a single RSS feed entry

        Args:
            entry: feedparser entry object
            feed_url: URL of the source feed

        Returns:
            Dictionary with parsed entry data
        """
        try:
            # Extract basic information
            title = entry.get('title', '')
            description = entry.get('description', '') or entry.get('summary', '')
            link = entry.get('link', '')

            # Parse published date
            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6])

            # Extract deal information from title and description
            deal_info = self._extract_deal_info(title, description)

            return {
                'title': title,
                'description': self._clean_html(description),
                'link': link,
                'published_date': published_date,
                'feed_url': feed_url,
                **deal_info
            }

        except Exception as e:
            print(f"Error parsing entry: {e}")
            return None

    def _extract_deal_info(self, title: str, description: str) -> Dict:
        """
        Extract deal-specific information from title and description

        Args:
            title: Entry title
            description: Entry description

        Returns:
            Dictionary with extracted deal information
        """
        text = f"{title} {description}"
        info = {
            'origin_airport': None,
            'destination_airport': None,
            'destination_city': None,
            'destination_region': None,
            'price': None,
            'points': None,
            'airline': None,
            'deal_type': None,
            'travel_class': None,
        }

        # Extract airports (3-letter IATA codes)
        airports = re.findall(r'\b([A-Z]{3})\b', text)
        if airports:
            info['origin_airport'] = airports[0] if len(airports) > 0 else None
            info['destination_airport'] = airports[1] if len(airports) > 1 else None

        # Extract price (e.g., $500, $1,234)
        price_match = re.search(r'\$(\d{1,3}(?:,\d{3})*)', text)
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            info['price'] = float(price_str)

        # Extract points/miles (e.g., 50,000 miles, 60K points)
        points_match = re.search(r'([\d,]+)\s*(?:K|k|,000)?\s*(?:points|miles)', text, re.IGNORECASE)
        if points_match:
            points_str = points_match.group(1).replace(',', '')
            if 'k' in text.lower():
                points_str += '000'
            info['points'] = int(points_str)

        # Detect region
        regions = {
            'Europe': ['europe', 'paris', 'london', 'rome', 'amsterdam', 'barcelona'],
            'Asia': ['asia', 'tokyo', 'seoul', 'singapore', 'bangkok', 'hong kong'],
            'South America': ['south america', 'brazil', 'argentina', 'peru', 'colombia'],
            'Africa': ['africa', 'morocco', 'south africa', 'egypt'],
            'Oceania': ['australia', 'new zealand', 'fiji', 'tahiti'],
        }

        text_lower = text.lower()
        for region, keywords in regions.items():
            if any(keyword in text_lower for keyword in keywords):
                info['destination_region'] = region
                break

        # Detect airlines
        airlines = ['delta', 'american', 'united', 'lufthansa', 'air france', 'klm', 'virgin atlantic']
        for airline in airlines:
            if airline in text_lower:
                info['airline'] = airline.title()
                break

        # Detect travel class
        if 'business' in text_lower or 'business class' in text_lower:
            info['travel_class'] = 'business'
        elif 'first class' in text_lower or 'first' in text_lower:
            info['travel_class'] = 'first'
        elif 'premium economy' in text_lower:
            info['travel_class'] = 'premium_economy'
        else:
            info['travel_class'] = 'economy'

        # Detect deal type
        if 'hotel' in text_lower:
            info['deal_type'] = 'hotel'
        elif 'cruise' in text_lower:
            info['deal_type'] = 'cruise'
        elif 'package' in text_lower:
            info['deal_type'] = 'package'
        else:
            info['deal_type'] = 'flight'

        return info

    def _clean_html(self, html_text: str) -> str:
        """Remove HTML tags from text"""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', html_text)

    def filter_msp_deals(self, entries: List[Dict]) -> List[Dict]:
        """
        Filter entries for deals from MSP airport

        Args:
            entries: List of RSS entries

        Returns:
            Filtered list containing only MSP deals
        """
        msp_deals = []

        for entry in entries:
            text = f"{entry['title']} {entry['description']}".upper()

            # Check if MSP is mentioned
            if 'MSP' in text or 'MINNEAPOLIS' in text or 'TWIN CITIES' in text:
                entry['is_msp_deal'] = True
                msp_deals.append(entry)
            # If origin airport is extracted and it's MSP
            elif entry.get('origin_airport') == 'MSP':
                entry['is_msp_deal'] = True
                msp_deals.append(entry)

        return msp_deals

    def get_latest_msp_deals(self, limit: int = 20) -> List[Dict]:
        """
        Get the latest travel deals from MSP

        Args:
            limit: Maximum number of deals to return

        Returns:
            List of latest MSP deals
        """
        all_entries = self.fetch_all_feeds()
        msp_deals = self.filter_msp_deals(all_entries)

        # Sort by published date (newest first)
        msp_deals.sort(
            key=lambda x: x['published_date'] if x['published_date'] else datetime.min,
            reverse=True
        )

        return msp_deals[:limit]


# Create singleton instance
rss_service = RSSService()
