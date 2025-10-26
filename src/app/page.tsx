"use client";

import { useCoAgent, useCopilotAction, useCopilotChat } from "@copilotkit/react-core";
import { CopilotKitCSSProperties, CopilotChat } from "@copilotkit/react-ui";
import { useState, useEffect } from "react";

export default function CopilotKitPage() {
  const [themeColor, setThemeColor] = useState("#6366f1");

  // 🪁 Frontend Actions: https://docs.copilotkit.ai/guides/frontend-actions
  useCopilotAction({
    name: "setThemeColor",
    parameters: [{
      name: "themeColor",
      description: "The theme color to set. Make sure to pick nice colors.",
      required: true,
    }],
    handler({ themeColor }) {
      setThemeColor(themeColor);
    },
  });

  return (
    <main style={{ "--copilot-kit-primary-color": themeColor } as CopilotKitCSSProperties}>
      <YourMainContent themeColor={themeColor} />
    </main>
  );
}

// State of the agent, make sure this aligns with your agent's state.
type AgentState = {
  proverbs: string[];
}

// Session type for chat history
type ChatSession = {
  id: string;
  title: string;
  timestamp: number;
  messages: unknown[];
}

function YourMainContent({ themeColor }: { themeColor: string }) {
  // 🪁 Shared State: https://docs.copilotkit.ai/coagents/shared-state
  const { state, setState } = useCoAgent<AgentState>({
    name: "my_agent",
    initialState: {
      proverbs: [
        "CopilotKit may be new, but its the best thing since sliced bread.",
      ],
    },
  })

  // Get chat context
  const chatContext = useCopilotChat();
  const chatMessages = chatContext.visibleMessages || [];

  // Session management state
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string>("");

  // Load sessions from localStorage on mount
  useEffect(() => {
    const loadSessions = async () => {
      try {
        const response = await fetch('/api/sessions');
        const data = await response.json();
        setSessions(data);
        if (data.length > 0) {
          setCurrentSessionId(data[0].id);
        }
      } catch (error) {
        console.error('Failed to load sessions:', error);
        // Fallback to creating initial session
        const newSession: ChatSession = {
          id: Date.now().toString(),
          title: "New Session",
          timestamp: Date.now(),
          messages: []
        };
        setSessions([newSession]);
        setCurrentSessionId(newSession.id);
        await fetch('/api/sessions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newSession)
        });
      }
    };
    loadSessions();
  }, []);

  // Save current chat messages to the active session
  useEffect(() => {
    if (chatMessages.length > 0 && currentSessionId) {
      const updateSession = async () => {
        const updatedSessions = sessions.map(session => {
          if (session.id === currentSessionId) {
            // Generate a title from the first user message
            const firstUserMsg = chatMessages.find((m) => {
              return (m as unknown as Record<string, unknown>).role === 'user';
            });
            
            let title = 'Chat Session';
            if (firstUserMsg) {
              const content = (firstUserMsg as unknown as Record<string, unknown>).content;
              if (typeof content === 'string') {
                title = content.substring(0, 30) + (content.length > 30 ? '...' : '');
              }
            }
            
            return {
              ...session,
              messages: chatMessages,
              title,
              timestamp: Date.now()
            };
          }
          return session;
        });
        
        setSessions(updatedSessions);
        
        // Save to server
        const currentSession = updatedSessions.find(s => s.id === currentSessionId);
        if (currentSession) {
          await fetch(`/api/sessions/${currentSessionId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentSession)
          });
        }
      };
      
      updateSession();
    }
  }, [chatMessages, currentSessionId, sessions]);

  // Create new session
  const createNewSession = async () => {
    const newSession: ChatSession = {
      id: Date.now().toString(),
      title: "New Session",
      timestamp: Date.now(),
      messages: []
    };
    
    // Save to server first
    try {
      await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSession)
      });
      
      // Then update local state
      const updated = [newSession, ...sessions];
      setSessions(updated);
      setCurrentSessionId(newSession.id);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  // Switch to a different session
  const switchSession = (sessionId: string) => {
    setCurrentSessionId(sessionId);
  };

  // Delete a session
  const deleteSession = async (sessionId: string) => {
    const updated = sessions.filter(s => s.id !== sessionId);
    setSessions(updated);
    
    // Delete from server
    await fetch(`/api/sessions/${sessionId}`, {
      method: 'DELETE'
    });
    
    if (currentSessionId === sessionId && updated.length > 0) {
      setCurrentSessionId(updated[0].id);
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  //🪁 Generative UI: https://docs.copilotkit.ai/coagents/generative-ui
  useCopilotAction({
    name: "get_weather",
    description: "Get the weather for a given location.",
    available: "disabled",
    parameters: [
      { name: "location", type: "string", required: true },
    ],
    render: ({ args }) => {
      return <WeatherCard location={args.location} themeColor={themeColor} />
    },
  });

  return (
    <div
      style={{ 
        backgroundImage: 'url(/knighthacks.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}
      className="h-screen w-screen flex justify-center items-center gap-4 transition-colors duration-300 p-4 relative"
    >
      {/* Color overlay for theme */}
      <div 
        style={{ backgroundColor: themeColor }}
        className="absolute inset-0 opacity-30 transition-colors duration-300"
      />
      
      {/* Content wrapper */}
      <div className="relative z-10 flex h-full w-full justify-center items-center gap-4">
      {/* Chat Sessions Sidebar */}
      <div className="h-full w-64 bg-white/10 backdrop-blur-md rounded-2xl shadow-xl p-4 overflow-y-auto flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white">Chat History</h2>
          <button
            onClick={createNewSession}
            className="bg-white/20 hover:bg-white/30 text-white rounded-lg px-3 py-1 text-sm font-semibold transition-all"
            title="New Session"
          >
            + New
          </button>
        </div>
        
        <div className="flex flex-col gap-2 flex-1 overflow-y-auto">
          {sessions.map((session) => (
            <div
              key={session.id}
              className={`p-3 rounded-lg cursor-pointer transition-all group relative ${
                session.id === currentSessionId
                  ? "bg-white/30 border-2 border-white/40"
                  : "bg-white/10 hover:bg-white/20 border-2 border-transparent"
              }`}
              onClick={() => session.id !== currentSessionId && switchSession(session.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-white font-medium text-sm truncate">
                    {session.title}
                  </p>
                  <p className="text-white/60 text-xs mt-1">
                    {formatTimestamp(session.timestamp)}
                  </p>
                  <p className="text-white/50 text-xs">
                    {session.messages.length} messages
                  </p>
                </div>
                {sessions.length > 1 && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteSession(session.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 transition-opacity ml-2 bg-red-500/80 hover:bg-red-600 text-white rounded-full h-5 w-5 flex items-center justify-center text-xs"
                    title="Delete session"
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>
          ))}
          {sessions.length === 0 && (
            <p className="text-white/60 text-sm italic text-center mt-4">
              No sessions yet
            </p>
          )}
        </div>
      </div>

      {/* Main Content Island */}
      <div className="bg-white/20 backdrop-blur-md p-8 rounded-2xl shadow-xl max-w-3xl w-full h-full flex flex-col">
        <h1 className="text-5xl font-black text-white mb-2 text-center uppercase tracking-wider" 
            style={{ 
              fontFamily: 'Impact, "Arial Black", sans-serif',
              textShadow: '3px 3px 0px rgba(0,0,0,0.3), 6px 6px 0px rgba(0,0,0,0.1)',
              letterSpacing: '0.05em'
            }}>
          Knightmare Protocol
        </h1>
        <p className="text-gray-200 text-center italic mb-6">Your AI-powered mission control 🎮</p>
        <hr className="border-white/20 my-6" />
        
        {/* Proverbs List */}
        <div className="flex flex-col gap-3 mb-6 overflow-y-auto flex-shrink-0" style={{ maxHeight: '30%' }}>
          {state.proverbs?.map((proverb, index) => (
            <div
              key={index}
              className="bg-white/15 p-4 rounded-xl text-white relative group hover:bg-white/20 transition-all"
            >
              <p className="pr-8">{proverb}</p>
              <button
                onClick={() => setState({
                  ...state,
                  proverbs: state.proverbs?.filter((_, i) => i !== index),
                })}
                className="absolute right-3 top-3 opacity-0 group-hover:opacity-100 transition-opacity
                  bg-red-500 hover:bg-red-600 text-white rounded-full h-6 w-6 flex items-center justify-center"
              >
                ✕
              </button>
            </div>
          ))}
        </div>

        {/* Chat Interface */}
        <div className="flex-1 min-h-0" key={`chat-wrapper-${currentSessionId}`}>
          <CopilotChat
            key={currentSessionId}
            className="h-full"
            labels={{
              title: "Chat Assistant",
              initial: "👋 Hi! I can help you manage proverbs, change themes, and more.\n\nTry:\n- \"Set the theme to orange\"\n- \"Write a proverb about AI\"\n- \"Get the weather in SF\""
            }}
          />
        </div>
      </div>
      </div>
    </div>
  );
}

// Simple sun icon for the weather card
function SunIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-14 h-14 text-yellow-200">
      <circle cx="12" cy="12" r="5" />
      <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" strokeWidth="2" stroke="currentColor" />
    </svg>
  );
}

// Weather card component where the location and themeColor are based on what the agent
// sets via tool calls.
function WeatherCard({ location, themeColor }: { location?: string, themeColor: string }) {
  return (
    <div
    style={{ backgroundColor: themeColor }}
    className="rounded-xl shadow-xl mt-6 mb-4 max-w-md w-full"
  >
    <div className="bg-white/20 p-4 w-full">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-white capitalize">{location}</h3>
          <p className="text-white">Current Weather</p>
        </div>
        <SunIcon />
      </div>

      <div className="mt-4 flex items-end justify-between">
        <div className="text-3xl font-bold text-white">70°</div>
        <div className="text-sm text-white">Clear skies</div>
      </div>

      <div className="mt-4 pt-4 border-t border-white">
        <div className="grid grid-cols-3 gap-2 text-center">
          <div>
            <p className="text-white text-xs">Humidity</p>
            <p className="text-white font-medium">45%</p>
          </div>
          <div>
            <p className="text-white text-xs">Wind</p>
            <p className="text-white font-medium">5 mph</p>
          </div>
          <div>
            <p className="text-white text-xs">Feels Like</p>
            <p className="text-white font-medium">72°</p>
          </div>
        </div>
      </div>
    </div>
  </div>
  );
}
