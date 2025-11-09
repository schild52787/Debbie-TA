"""Legal research service for airline/hotel policies and regulations"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime

from config.settings import settings


class LegalResearchService:
    """Service for researching travel-related laws and policies"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.USER_AGENT
        })

    def get_dot_regulations(self) -> Dict:
        """
        Fetch current DOT (Department of Transportation) regulations

        Returns:
            Dictionary with DOT regulation information
        """
        regulations = {
            'source': 'US Department of Transportation',
            'url': 'https://www.transportation.gov/airconsumer',
            'last_updated': datetime.now().isoformat(),
            'key_regulations': []
        }

        # Key DOT regulations for air travel
        key_regs = [
            {
                'title': '14 CFR Part 259 - Tarmac Delay',
                'description': 'Airlines must allow passengers to deplane after 3 hours (domestic) or 4 hours (international) on tarmac',
                'url': 'https://www.ecfr.gov/current/title-14/chapter-II/subchapter-A/part-259',
            },
            {
                'title': '14 CFR Part 250 - Oversales/Denied Boarding',
                'description': 'Compensation requirements for involuntary denied boarding',
                'url': 'https://www.ecfr.gov/current/title-14/chapter-II/subchapter-A/part-250',
            },
            {
                'title': 'Fly Rights - Air Passenger Rights',
                'description': 'Comprehensive guide to air passenger rights',
                'url': 'https://www.transportation.gov/sites/dot.gov/files/docs/resources/individuals/aviation-consumer-protection/302371/fly-rights-508.pdf',
            },
        ]

        regulations['key_regulations'] = key_regs

        return regulations

    def get_eu261_regulations(self) -> Dict:
        """
        Fetch EU261/2004 flight compensation regulations

        Returns:
            Dictionary with EU261 regulation information
        """
        regulations = {
            'source': 'European Union Regulation 261/2004',
            'url': 'https://europa.eu/youreurope/citizens/travel/passenger-rights/air/index_en.htm',
            'last_updated': datetime.now().isoformat(),
            'compensation_rules': {
                'description': 'EU regulation for flight delays, cancellations, and denied boarding',
                'eligibility': [
                    'Flight departs from EU airport (any airline)',
                    'Flight arrives at EU airport on EU airline',
                    'Delay of 3+ hours at final destination',
                    'Cancellation with less than 14 days notice',
                ],
                'compensation_amounts': {
                    'under_1500km': '€250',
                    '1500_3500km': '€400',
                    'over_3500km': '€600',
                },
                'additional_rights': [
                    'Right to care (meals, refreshments, accommodation)',
                    'Right to reimbursement or re-routing',
                    'Right to information',
                ],
            }
        }

        return regulations

    def get_airline_contract_of_carriage(self, airline: str) -> Optional[Dict]:
        """
        Fetch airline's Contract of Carriage

        Args:
            airline: Airline name (e.g., "Delta", "American")

        Returns:
            Dictionary with contract of carriage information
        """
        # URLs for major airlines' contracts of carriage
        airline_urls = {
            'delta': {
                'name': 'Delta Air Lines',
                'url': 'https://www.delta.com/us/en/legal/contract-of-carriage-dom',
                'international_url': 'https://www.delta.com/us/en/legal/contract-of-carriage-intl',
            },
            'american': {
                'name': 'American Airlines',
                'url': 'https://www.aa.com/i18n/customer-service/support/conditions-of-carriage.jsp',
            },
            'united': {
                'name': 'United Airlines',
                'url': 'https://www.united.com/ual/en/us/fly/contract-of-carriage.html',
            },
        }

        airline_key = airline.lower()

        if airline_key not in airline_urls:
            return None

        airline_info = airline_urls[airline_key]

        contract = {
            'airline': airline_info['name'],
            'url': airline_info['url'],
            'last_checked': datetime.now().isoformat(),
            'key_sections': self._get_key_contract_sections(airline_key),
        }

        return contract

    def _get_key_contract_sections(self, airline: str) -> List[Dict]:
        """Get key sections of airline contract of carriage"""
        # Placeholder - in production, this would scrape the actual contract
        common_sections = [
            {
                'rule': 'Rule 24 - Refunds',
                'summary': 'Conditions under which refunds are provided',
                'relevance': 'cancellation, refund_request',
            },
            {
                'rule': 'Rule 25 - Denied Boarding Compensation',
                'summary': 'Compensation for involuntary denied boarding',
                'relevance': 'overbooking',
            },
            {
                'rule': 'Rule 27 - Schedule Changes and Flight Cancellations',
                'summary': 'Airline obligations for schedule changes and cancellations',
                'relevance': 'flight_cancellation, flight_delay',
            },
            {
                'rule': 'Rule 120 - Baggage',
                'summary': 'Baggage liability and compensation limits',
                'relevance': 'lost_luggage, damaged_luggage',
            },
        ]

        return common_sections

    def get_hotel_policy(self, hotel_chain: str) -> Optional[Dict]:
        """
        Fetch hotel chain's cancellation and service policies

        Args:
            hotel_chain: Hotel chain name (e.g., "Marriott", "Hyatt")

        Returns:
            Dictionary with hotel policy information
        """
        # URLs for major hotel chains
        hotel_urls = {
            'marriott': {
                'name': 'Marriott International',
                'cancellation_policy_url': 'https://www.marriott.com/reservation/terms-and-conditions.mi',
                'guarantee_url': 'https://www.marriott.com/loyalty/terms/default.mi',
            },
            'hyatt': {
                'name': 'Hyatt Hotels',
                'cancellation_policy_url': 'https://www.hyatt.com/en-US/customer-care/terms-of-use',
            },
        }

        hotel_key = hotel_chain.lower()

        if hotel_key not in hotel_urls:
            return None

        hotel_info = hotel_urls[hotel_key]

        policy = {
            'hotel_chain': hotel_info['name'],
            'url': hotel_info.get('cancellation_policy_url'),
            'last_checked': datetime.now().isoformat(),
            'key_policies': [
                {
                    'type': 'Cancellation Policy',
                    'summary': 'Standard cancellation is 24-48 hours before check-in',
                },
                {
                    'type': 'Service Guarantee',
                    'summary': 'Many chains offer service guarantees for issues',
                },
            ],
        }

        return policy

    def research_dispute_legal_options(
        self,
        provider_type: str,
        provider_name: str,
        issue_type: str,
        route: Optional[str] = None
    ) -> Dict:
        """
        Comprehensive legal research for a dispute

        Args:
            provider_type: 'airline' or 'hotel'
            provider_name: Name of airline/hotel
            issue_type: Type of issue
            route: Flight route if applicable (e.g., "MSP-CDG")

        Returns:
            Comprehensive research report
        """
        report = {
            'provider_type': provider_type,
            'provider_name': provider_name,
            'issue_type': issue_type,
            'route': route,
            'applicable_laws': [],
            'provider_policy': None,
            'recommended_actions': [],
            'generated_at': datetime.now().isoformat(),
        }

        # Determine applicable laws
        if provider_type == 'airline':
            # Always applicable: DOT regulations
            dot_regs = self.get_dot_regulations()
            report['applicable_laws'].append({
                'law': 'US DOT Regulations',
                'data': dot_regs,
                'applicability': 'Always applicable for US flights',
            })

            # Check if EU261 applies
            if route and self._is_eu_route(route):
                eu261 = self.get_eu261_regulations()
                report['applicable_laws'].append({
                    'law': 'EU Regulation 261/2004',
                    'data': eu261,
                    'applicability': 'Applies to flights to/from EU',
                })

            # Get airline's contract of carriage
            contract = self.get_airline_contract_of_carriage(provider_name)
            if contract:
                report['provider_policy'] = contract

        elif provider_type == 'hotel':
            # Get hotel policy
            policy = self.get_hotel_policy(provider_name)
            if policy:
                report['provider_policy'] = policy

        # Generate recommended actions based on issue type
        report['recommended_actions'] = self._get_recommended_actions(
            provider_type, issue_type, report['applicable_laws']
        )

        return report

    def _is_eu_route(self, route: str) -> bool:
        """Check if route involves EU airports"""
        eu_airports = [
            'CDG', 'ORY',  # Paris
            'LHR', 'LGW', 'STN',  # London
            'AMS',  # Amsterdam
            'FRA',  # Frankfurt
            'MAD',  # Madrid
            'BCN',  # Barcelona
            'FCO',  # Rome
            'MUC',  # Munich
            'VIE',  # Vienna
            'BRU',  # Brussels
            'DUB',  # Dublin
            'ZRH',  # Zurich (not EU but follows EU261)
        ]

        route_airports = route.split('-')
        return any(airport in eu_airports for airport in route_airports)

    def _get_recommended_actions(
        self,
        provider_type: str,
        issue_type: str,
        applicable_laws: List[Dict]
    ) -> List[str]:
        """Generate recommended actions based on issue type and applicable laws"""
        actions = []

        if provider_type == 'airline':
            if issue_type in ['flight_cancellation', 'flight_delay']:
                actions.append('File claim with airline customer relations')

                # Check if EU261 applies
                if any('EU' in law['law'] for law in applicable_laws):
                    actions.append('File EU261 compensation claim')

                actions.append('Document all expenses (meals, hotel, transportation)')
                actions.append('Request refund or rebooking per DOT regulations')

            elif issue_type == 'lost_luggage':
                actions.append('File baggage claim immediately (must be within 24 hours)')
                actions.append('Document contents and value')
                actions.append('Request interim expense reimbursement')

            elif issue_type == 'overbooking':
                actions.append('Request denied boarding compensation per DOT Part 250')
                actions.append('Get written confirmation of compensation amount')

        elif provider_type == 'hotel':
            if issue_type in ['service_complaint', 'hotel_issue']:
                actions.append('Contact hotel manager immediately')
                actions.append('Document issue with photos if applicable')
                actions.append('Request written incident report')
                actions.append('Follow up with corporate customer service')

        # General actions
        actions.append('Keep all receipts and documentation')
        actions.append('File complaint with DOT/BBB if unresolved')

        return actions


# Create singleton instance
legal_research_service = LegalResearchService()
