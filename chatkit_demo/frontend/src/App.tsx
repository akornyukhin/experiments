import {ChatKit, useChatKit} from "@openai/chatkit-react";

function App() {
  const domainKey = import.meta.env.VITE_CHATKIT_DOMAIN_KEY;

  if (!domainKey && !import.meta.env.DEV) {
    throw new Error("VITE_CHATKIT_DOMAIN_KEY must be set outside local development.");
  }

  const chatkit = useChatKit({
    api: {
      url: "/chatkit",
      domainKey: domainKey ?? "local-dev",
    },
    onError: ({error}) => {
      console.error("ChatKit error", error);
    },
    history: {
      enabled: true,
    },
  });

  return (
    <ChatKit
      control={chatkit.control}
      style={{display: "block", width: "100%", minHeight: "100svh"}}
    />
  );
}

export default App
