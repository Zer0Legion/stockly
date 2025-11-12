import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function UserStockForm() {
  const [userRequests, setUserRequests] = useState([
    {
      email: "",
      name: "",
      stocks: [{ exchange: "", ticker: "" }],
    },
  ]);

  const handleUserChange = (index, field, value) => {
    const updated = [...userRequests];
    updated[index][field] = value;
    setUserRequests(updated);
  };

  const handleStockChange = (userIndex, stockIndex, field, value) => {
    const updated = [...userRequests];
    updated[userIndex].stocks[stockIndex][field] = value;
    setUserRequests(updated);
  };

  const addUserRequest = () => {
    setUserRequests([
      ...userRequests,
      { email: "", name: "", stocks: [{ exchange: "", ticker: "" }] },
    ]);
  };

  const addStock = (userIndex) => {
    const updated = [...userRequests];
    updated[userIndex].stocks.push({ exchange: "", ticker: "" });
    setUserRequests(updated);
  };

  const validateEmail = (email) =>
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  const handleSubmit = async () => {
    for (const user of userRequests) {
      if (!validateEmail(user.email)) {
        alert(`Invalid email: ${user.email}`);
        return;
      }
      if (!user.name.trim()) {
        alert("Name cannot be empty");
        return;
      }
      if (!user.stocks.length) {
        alert("Each user must have at least one stock");
        return;
      }
      for (const stock of user.stocks) {
        if (!stock.exchange || !stock.ticker) {
          alert("Stock exchange and ticker cannot be empty");
          return;
        }
      }
    }

    try {
      const res = await fetch(`${API_URL}/send_email`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_requests: userRequests }),
      });

      if (!res.ok) throw new Error("Failed to submit data");
      alert("Submitted successfully!");
    } catch (err) {
      console.error(err);
      alert("Submission failed");
    }
  };

  return (
    <div className="p-6 space-y-6">
      {userRequests.map((user, userIdx) => (
        <div
          key={userIdx}
          className="border p-6 rounded-2xl shadow space-y-6 bg-white"
        >
          <div className="space-y-4 border-b pb-4">
            <h2 className="text-lg font-semibold text-gray-700">User Info</h2>
            <Input
              placeholder="Email"
              type="email"
              value={user.email}
              onChange={(e) => handleUserChange(userIdx, "email", e.target.value)}
            />
            <Input
              placeholder="Name"
              value={user.name}
              onChange={(e) => handleUserChange(userIdx, "name", e.target.value)}
            />
          </div>

          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-700">Stocks</h2>
            {user.stocks.map((stock, stockIdx) => (
              <div key={stockIdx} className="flex gap-2">
                <Input
                  placeholder="Exchange"
                  value={stock.exchange}
                  onChange={(e) =>
                    handleStockChange(userIdx, stockIdx, "exchange", e.target.value)
                  }
                />
                <Input
                  placeholder="Ticker"
                  value={stock.ticker}
                  onChange={(e) =>
                    handleStockChange(userIdx, stockIdx, "ticker", e.target.value)
                  }
                />
              </div>
            ))}
            <Button onClick={() => addStock(userIdx)}>Add Stock</Button>
          </div>
        </div>
      ))}
      <div className="space-x-2">
        <Button onClick={addUserRequest}>Add User Request</Button>
        <Button onClick={handleSubmit}>Submit</Button>
      </div>
    </div>
  );
}