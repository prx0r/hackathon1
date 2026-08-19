import unittest
from patala_research_ci.mcp_gateway import StreamableHTTPClient, TrustedMCPServer

class MCPGatewayTests(unittest.TestCase):
    def test_sse_final_response(self):
        raw=b'data: {"jsonrpc":"2.0","method":"notifications/progress"}\n\ndata: {"jsonrpc":"2.0","id":7,"result":{"ok":true}}\n\n'
        obj=StreamableHTTPClient._parse_body('text/event-stream',raw,7)
        self.assertTrue(obj['result']['ok'])
    def test_requires_https(self):
        with self.assertRaises(ValueError): TrustedMCPServer(url='http://example.com/mcp').validate_url()

if __name__=='__main__': unittest.main()
