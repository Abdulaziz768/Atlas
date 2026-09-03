
from atlas.ingestion.client import APIClient
from atlas.ingestion.company import CompanyService

def test_atlas_import():
	import atlas
	assert atlas is not None 

def test_api_client_builds_url():
	client = APIClient("https://example.com/api")
	assert client.base_url == "https://example.com/api"

class FakeAPIClient:
	def get(self, endpoint, params=None):
		return {
			"Symbol": "AAPL",
			"Name": "Apple Inc.",
			"Exchange": "NASDAQ",
			"Sector": "TECHNOLOGY",
			"Industry": "CONSUMER ELECTRONICS",
			"Currency": "USD",
			"MarketCapitalization": "3000000000000",
			"Description": "Technology company",
		}
	
def test_company_service():
	client = FakeAPIClient()
	service = CompanyService(client)

	company = service.get_company("AAPL")

	assert company.ticker == "AAPL"
	assert company.name == "Apple Inc."
	assert company.exchange == "NASDAQ"
	assert company.currency == "USD"