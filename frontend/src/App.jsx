import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import "./App.css";

const API_URL = "http://localhost:8000";

function App() {
  const [stocks, setStocks] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState("AAPL");
  const [stock, setStock] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/stocks`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch stocks");
        }
        return response.json();
      })
      .then((data) => {
        setStocks(data);
        if (data.length > 0) {
          setSelectedTicker(data[0].ticker);
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedTicker) return;

    setLoading(true);
    setError(null);

    fetch(`${API_URL}/stocks/${selectedTicker}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch stock data");
        }
        return response.json();
      })
      .then((data) => setStock(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [selectedTicker]);

  if (loading && !stock) {
    return <div className="status">Loading Atlas...</div>;
  }

  if (error) {
    return <div className="status error">{error}</div>;
  }

  if (!stock) {
    return <div className="status">No stock data available.</div>;
  }

  const chartData = [
    {
      name: "First Close",
      value: Number(stock.first_close),
    },
    {
      name: "Latest Close",
      value: Number(stock.latest_close),
    },
  ];

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>ATLAS</h1>
          <p>Financial Analytics Dashboard</p>
        </div>

        <select
          value={selectedTicker}
          onChange={(event) => setSelectedTicker(event.target.value)}
        >
          {stocks.map((item) => (
            <option key={item.ticker} value={item.ticker}>
              {item.ticker}
            </option>
          ))}
        </select>
      </header>

      <main>
        <section className="hero">
          <h2>{stock.ticker}</h2>
          <p>
            {stock.first_date} → {stock.latest_date}
          </p>
        </section>

        <section className="metrics">
          <MetricCard
            title="Latest Close"
            value={`$${Number(stock.latest_close).toFixed(2)}`}
          />

          <MetricCard
            title="Total Return"
            value={`${Number(stock.total_return_pct).toFixed(2)}%`}
          />

          <MetricCard
            title="Trading Days"
            value={stock.trading_days}
          />

          <MetricCard
            title="Total Volume"
            value={Number(stock.total_volume).toLocaleString()}
          />
        </section>

        <section className="content-grid">
          <div className="card chart-card">
            <h3>Price Comparison</h3>

            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h3>Performance</h3>

            <div className="stat">
              <span>First Close</span>
              <strong>${Number(stock.first_close).toFixed(2)}</strong>
            </div>

            <div className="stat">
              <span>Latest Close</span>
              <strong>${Number(stock.latest_close).toFixed(2)}</strong>
            </div>

            <div className="stat">
              <span>Average Daily Return</span>
              <strong>
                {Number(stock.average_daily_return_pct).toFixed(2)}%
              </strong>
            </div>

            <div className="stat">
              <span>Best Day</span>
              <strong>
                {Number(stock.best_day_return_pct).toFixed(2)}%
              </strong>
            </div>

            <div className="stat">
              <span>Worst Day</span>
              <strong>
                {Number(stock.worst_day_return_pct).toFixed(2)}%
              </strong>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

function MetricCard({ title, value }) {
  return (
    <div className="metric-card">
      <span>{title}</span>
      <strong>{value}</strong>
    </div>
  );
}

export default App;
