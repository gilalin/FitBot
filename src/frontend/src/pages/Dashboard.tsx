import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

interface DashboardStats {
  totalMembers: number;
  activeMembers: number;
  totalRevenue: number;
  membershipBreakdown: {
    type: string;
    count: number;
  }[];
  attendanceData: {
    date: string;
    attendance: number;
  }[];
  revenueData: {
    month: string;
    amount: number;
  }[];
}

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  progress?: number;
}

function MetricCard({ title, value, subtitle, progress }: MetricCardProps) {
  return (
    <Card>
      <CardContent>
        <Typography color="textSecondary" gutterBottom>
          {title}
        </Typography>
        <Typography variant="h4" component="div">
          {value}
        </Typography>
        {subtitle && (
          <Typography color="textSecondary" sx={{ mb: 1.5 }}>
            {subtitle}
          </Typography>
        )}
        {progress !== undefined && (
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{ mt: 2 }}
          />
        )}
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: () => api.get('/dashboard/stats').then((res) => res.data),
  });

  if (isLoading) return <div>Loading...</div>;

  const membershipUtilization =
    stats ? (stats.activeMembers / stats.totalMembers) * 100 : 0;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Total Members"
            value={stats?.totalMembers || 0}
            subtitle="All time"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Active Members"
            value={stats?.activeMembers || 0}
            subtitle="Current month"
            progress={membershipUtilization}
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Monthly Revenue"
            value={`$${stats?.totalRevenue.toLocaleString() || 0}`}
            subtitle="Current month"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Class Attendance"
            value={
              stats?.attendanceData[stats.attendanceData.length - 1]?.attendance ||
              0
            }
            subtitle="Today"
          />
        </Grid>

        {/* Membership Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Membership Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats?.membershipBreakdown}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="type" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Attendance Trend */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Attendance Trend
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={stats?.attendanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="attendance"
                    stroke="#82ca9d"
                    activeDot={{ r: 8 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Revenue Chart */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Revenue Trend
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats?.revenueData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="amount" fill="#3f51b5" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
} 