import { useState, useRef, useEffect } from "react";
import "./App.css";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

const Message = ({ msg }: { msg: ChatMessage }) => (
  <>
    <div
      className={`p-2 border rounded-md max-w-[200px] break-words text-left whitespace-pre-wrap
      ${msg.role === "user" ? "ml-auto bg-green-300" : "mr-auto bg-cyan-300"}
    `}
    >
      {msg.content}
    </div>
  </>
);

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      content: "Hi, I am your friendly assistant, how can I help?",
      role: "assistant",
    },
  ]);

  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTo({
        top: containerRef.current.scrollHeight,
        behavior: "smooth", // Smooth scrolling
      });
    }
  }, [messages]);

  console.log(messages);

  return (
    <div className="flex flex-col gap-5 items-center">
      <div className="text-2xl font-bold">Sample Chat App</div>
      <div
        ref={containerRef}
        className="flex flex-col gap-3 bg-gray-100 h-[400px] w-3/5 rounded-lg p-5 overflow-y-auto"
      >
        {messages.map((msg, idx) => {
          return <Message msg={msg} key={`msg-${idx}`} />;
        })}
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault(); // Prevent the default form submission
          // @ts-ignore
          const inputField = e.target.message; // Get the input element
          const message = inputField.value; // Get the value of the input element

          setMessages((prevMessages) => [
            ...prevMessages,
            { content: message, role: "user" },
          ]);

          fetch("http://localhost:8000/send_message", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              messages: [...messages, { content: message, role: "user" }],
            }),
          })
            .then((response) => {
              if (!response.ok) {
                throw new Error("Network response was not ok");
              }
              return response.json();
            })
            .then((data) => {
              console.log("Success:", data);
              inputField.value = "";
              setMessages((prevMessages) => [...prevMessages, data]);
            })
            .catch((error) => {
              console.error("Error:", error);
            });
        }}
      >
        <label htmlFor="message">Message:</label>
        <textarea
          id="message"
          name="message"
          required
          className="p-2 border rounded-md"
          onKeyDown={(e) => {
            if (e.metaKey && e.key === "Enter") {
              e.preventDefault(); // Prevent newline insertion
              // @ts-ignore
              e.target.form.requestSubmit(); // Trigger form submission
            }
          }}
        />
        <button type="submit" className="p-2 border rounded-md">
          Send
        </button>
      </form>
    </div>
  );
}

export default App;
