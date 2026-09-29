/**
 * Cloudflare Worker Proxy for Lucid Motors Mobile API
 * Handles CORS and token proxying securely without storing credentials.
 */

export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);

  // CORS headers
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, x-lucid-client-version',
    'Content-Type': 'application/json'
  };

  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const action = url.searchParams.get('action') || 'telemetry';

    // Route: Authenticate against Lucid AWS Cognito
    if (action === 'auth' && request.method === 'POST') {
      const body = await request.json();
      const { username, password, region = 'us-east-1' } = body;

      if (!username || !password) {
        return new Response(JSON.stringify({ error: 'Missing credentials' }), {
          status: 400,
          headers: corsHeaders
        });
      }

      // AWS Cognito User Pool Client ID for Lucid Motors App
      // Lucid Mobile Client ID: 2k74s1e56m7uv1f3n1b2723t4m (standard iOS mobile client ID)
      const cognitoEndpoint = `https://cognito-idp.${region}.amazonaws.com/`;
      
      const authPayload = {
        AuthFlow: 'USER_PASSWORD_AUTH',
        ClientId: '2k74s1e56m7uv1f3n1b2723t4m',
        AuthParameters: {
          USERNAME: username,
          PASSWORD: password
        }
      };

      try {
        const cognitoResp = await fetch(cognitoEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth'
          },
          body: JSON.stringify(authPayload)
        });

        const cognitoData = await cognitoResp.json();
        return new Response(JSON.stringify(cognitoData), {
          status: cognitoResp.status,
          headers: corsHeaders
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: 'Cognito authentication proxy failed', details: err.message }), {
          status: 502,
          headers: corsHeaders
        });
      }
    }

    // Route: Query Vehicle Telemetry
    if (action === 'telemetry') {
      const authHeader = request.headers.get('Authorization');
      const vin = url.searchParams.get('vin');

      if (!authHeader) {
        return new Response(JSON.stringify({ error: 'Authorization header required' }), {
          status: 401,
          headers: corsHeaders
        });
      }

      const lucidGateway = vin 
        ? `https://api.lucidmotors.com/v1/vehicles/${vin}/state`
        : `https://api.lucidmotors.com/v1/users/me/vehicles`;

      const gatewayResp = await fetch(lucidGateway, {
        headers: {
          'Authorization': authHeader,
          'Accept': 'application/json',
          'User-Agent': 'LucidApp/2.24.0 (iPhone; iOS 18.0; Scale/3.00)'
        }
      });

      const gatewayData = await gatewayResp.json();
      return new Response(JSON.stringify(gatewayData), {
        status: gatewayResp.status,
        headers: corsHeaders
      });
    }

    return new Response(JSON.stringify({ error: 'Unsupported action' }), {
      status: 400,
      headers: corsHeaders
    });

  } catch (globalErr) {
    return new Response(JSON.stringify({ error: globalErr.message }), {
      status: 500,
      headers: corsHeaders
    });
  }
}
