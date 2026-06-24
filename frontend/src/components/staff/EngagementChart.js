"use client";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  BarChart, Bar, PieChart, Pie, Cell, Legend,
} from "recharts";
import { PIE_COLORS } from "@/lib/constants";

const AXIS = { fontSize: 12, fill: "#8A8AA3" };

export function LineTrend({ data, dataKey = "value", xKey = "name", color = "#1A237E", height = 240 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 10, right: 10, left: -16, bottom: 0 }}>
        <defs>
          <linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.3} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#EEE" vertical={false} />
        <XAxis dataKey={xKey} tick={AXIS} axisLine={false} tickLine={false} />
        <YAxis tick={AXIS} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={{ borderRadius: 12, border: "none", boxShadow: "var(--shadow-md)" }} />
        <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={3}
          dot={{ r: 4, fill: color }} activeDot={{ r: 6 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function BarChartCard({ data, dataKey = "value", xKey = "name", color = "#3F51B5", height = 240 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#EEE" vertical={false} />
        <XAxis dataKey={xKey} tick={AXIS} axisLine={false} tickLine={false} />
        <YAxis tick={AXIS} axisLine={false} tickLine={false} allowDecimals={false} />
        <Tooltip contentStyle={{ borderRadius: 12, border: "none", boxShadow: "var(--shadow-md)" }}
          cursor={{ fill: "rgba(26,35,126,0.05)" }} />
        <Bar dataKey={dataKey} fill={color} radius={[8, 8, 0, 0]} maxBarSize={48} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function PieChartCard({ data, height = 240 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={84}
          paddingAngle={3}>
          {data.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
        </Pie>
        <Tooltip contentStyle={{ borderRadius: 12, border: "none", boxShadow: "var(--shadow-md)" }} />
        <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
      </PieChart>
    </ResponsiveContainer>
  );
}
