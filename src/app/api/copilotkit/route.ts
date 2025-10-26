import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";
import { NextRequest } from "next/server";

// Determine the agent URL based on environment
// In production (Vercel), use the Render backend
// In development, use localhost
const getAgentUrl = () => {
  // Use Render URL for production, localhost for development
  return process.env.NODE_ENV === 'production' 
    ? "https://aiagentic.onrender.com/"
    : "http://localhost:8000/";
};
 
// 1. You can use any service adapter here for multi-agent support. We use
//    the empty adapter since we're only using one agent.
const serviceAdapter = new ExperimentalEmptyAdapter();
 
// 2. Create the CopilotRuntime instance and utilize the AG-UI client
//    to setup the connection with the ADK agent.
const runtime = new CopilotRuntime({
  agents: {
    // Our FastAPI endpoint URL (dynamic based on environment)
    "my_agent": new HttpAgent({url: getAgentUrl()}),
  }   
});
 
// 3. Build a Next.js API route that handles the CopilotKit runtime requests.
export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime, 
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });
 
  return handleRequest(req);
};