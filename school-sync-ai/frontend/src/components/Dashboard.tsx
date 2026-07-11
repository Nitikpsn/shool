import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, CartesianGrid } from 'recharts'

interface DashboardProps {
  stats: {
    boys: number
    girls: number
    sc: number
    obc: number
    st: number
    ews: number
    gen: number
    total: number
  }
}

const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899']

export default function Dashboard({ stats }: DashboardProps) {
  const genderData = [
    { name: 'Boys', value: stats.boys },
    { name: 'Girls', value: stats.girls },
  ]

  const categoryData = [
    { name: 'SC', value: stats.sc },
    { name: 'ST', value: stats.st },
    { name: 'OBC', value: stats.obc },
    { name: 'EWS', value: stats.ews },
    { name: 'GEN', value: stats.gen },
  ].filter(d => d.value > 0)

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
      <div className="bg-white rounded-xl border p-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Gender Distribution</h3>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie data={genderData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label>
              {genderData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
            </Pie>
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-xl border p-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Category Distribution</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={categoryData}>
            <CartesianGrid strokeDasharray="3 3" />
            <Tooltip />
            <XAxis dataKey="name" />
            <YAxis />
            <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}