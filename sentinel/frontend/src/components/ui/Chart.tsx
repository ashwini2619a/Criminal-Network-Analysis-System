import React from 'react';
import {
  BarChart as RechartsBarChart, Bar,
  LineChart as RechartsLineChart, Line,
  PieChart as RechartsPieChart, Pie, Cell,
  AreaChart as RechartsAreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Legend
} from 'recharts';

const COLORS = ['#0284c7', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6', '#6366f1'];
const LIGHT_GRID = 'rgba(229, 231, 235, 0.8)';
const TEXT_COLOR = '#6b7280';

export const BarChart = ({ data, dataKeyX, dataKeyY, height = 300 }: any) => (
  <ResponsiveContainer width="100%" height={height}>
    <RechartsBarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
      <CartesianGrid strokeDasharray="3 3" stroke={LIGHT_GRID} vertical={false} />
      <XAxis dataKey={dataKeyX} stroke={TEXT_COLOR} fontSize={12} tickLine={false} axisLine={false} />
      <YAxis stroke={TEXT_COLOR} fontSize={12} tickLine={false} axisLine={false} />
      <RechartsTooltip 
        contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e5e7eb', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }} 
        itemStyle={{ color: '#111827' }} 
      />
      <Bar dataKey={dataKeyY} fill="#0284c7" radius={[4, 4, 0, 0]} />
    </RechartsBarChart>
  </ResponsiveContainer>
);

export const LineChart = ({ data, dataKeyX, dataKeyY, height = 300 }: any) => (
  <ResponsiveContainer width="100%" height={height}>
    <RechartsLineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
      <CartesianGrid strokeDasharray="3 3" stroke={LIGHT_GRID} vertical={false} />
      <XAxis dataKey={dataKeyX} stroke={TEXT_COLOR} fontSize={12} tickLine={false} axisLine={false} />
      <YAxis stroke={TEXT_COLOR} fontSize={12} tickLine={false} axisLine={false} />
      <RechartsTooltip 
        contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e5e7eb', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }} 
        itemStyle={{ color: '#111827' }} 
      />
      <Line type="monotone" dataKey={dataKeyY} stroke="#ef4444" strokeWidth={3} dot={{ r: 4, fill: '#ef4444' }} activeDot={{ r: 6 }} />
    </RechartsLineChart>
  </ResponsiveContainer>
);

export const PieChart = ({ data, dataKey, nameKey, height = 300 }: any) => (
  <ResponsiveContainer width="100%" height={height}>
    <RechartsPieChart>
      <Pie
        data={data}
        cx="50%"
        cy="50%"
        innerRadius={60}
        outerRadius={80}
        paddingAngle={5}
        dataKey={dataKey}
        nameKey={nameKey}
      >
        {data.map((_: any, index: number) => (
          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
        ))}
      </Pie>
      <RechartsTooltip 
        contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e5e7eb', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }} 
        itemStyle={{ color: '#111827' }} 
      />
      <Legend wrapperStyle={{ color: TEXT_COLOR }} />
    </RechartsPieChart>
  </ResponsiveContainer>
);

export const AreaChart = ({ data, dataKeyX, dataKeyY, height = 300 }: any) => (
  <ResponsiveContainer width="100%" height={height}>
    <RechartsAreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
      <defs>
        <linearGradient id="colorY" x1="0" y1="0" x2="0" y2="1">
          <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
          <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
        </linearGradient>
      </defs>
      <CartesianGrid strokeDasharray="3 3" stroke={LIGHT_GRID} vertical={false} />
      <XAxis dataKey={dataKeyX} stroke={TEXT_COLOR} fontSize={12} tickLine={false} axisLine={false} />
      <YAxis stroke={TEXT_COLOR} fontSize={12} tickLine={false} axisLine={false} />
      <RechartsTooltip 
        contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e5e7eb', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }} 
        itemStyle={{ color: '#111827' }} 
      />
      <Area type="monotone" dataKey={dataKeyY} stroke="#10b981" fillOpacity={1} fill="url(#colorY)" />
    </RechartsAreaChart>
  </ResponsiveContainer>
);
