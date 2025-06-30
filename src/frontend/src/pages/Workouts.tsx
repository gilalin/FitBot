import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
} from '@mui/material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';

interface Workout {
  id: string;
  name: string;
  description: string;
  type: 'AMRAP' | 'FOR_TIME' | 'EMOM';
  scheduledDate: string;
  coach: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function Workouts() {
  const [open, setOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [newWorkout, setNewWorkout] = useState<Partial<Workout>>({
    type: 'AMRAP',
  });

  const queryClient = useQueryClient();

  const { data: workouts, isLoading } = useQuery<Workout[]>({
    queryKey: ['workouts'],
    queryFn: () => api.get('/workouts').then((res) => res.data),
  });

  const createWorkoutMutation = useMutation({
    mutationFn: (workout: Partial<Workout>) =>
      api.post('/workouts', workout).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workouts'] });
      setOpen(false);
      setNewWorkout({ type: 'AMRAP' });
    },
  });

  const handleCreateWorkout = () => {
    createWorkoutMutation.mutate(newWorkout);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Workouts</Typography>
        <Button variant="contained" onClick={() => setOpen(true)}>
          Create Workout
        </Button>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Today's WOD" />
          <Tab label="Schedule" />
          <Tab label="History" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          {workouts
            ?.filter(
              (workout) =>
                new Date(workout.scheduledDate).toDateString() ===
                new Date().toDateString()
            )
            .map((workout) => (
              <Grid item xs={12} key={workout.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h5" gutterBottom>
                      {workout.name}
                    </Typography>
                    <Typography
                      variant="subtitle1"
                      color="text.secondary"
                      gutterBottom
                    >
                      {workout.type} - Coach: {workout.coach}
                    </Typography>
                    <Typography
                      variant="body1"
                      sx={{ whiteSpace: 'pre-line' }}
                    >
                      {workout.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          {workouts?.map((workout) => (
            <Grid item xs={12} sm={6} md={4} key={workout.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{workout.name}</Typography>
                  <Typography color="text.secondary" gutterBottom>
                    {new Date(workout.scheduledDate).toLocaleDateString()}
                  </Typography>
                  <Typography variant="body2">{workout.description}</Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          {workouts
            ?.filter(
              (workout) =>
                new Date(workout.scheduledDate) < new Date()
            )
            .map((workout) => (
              <Grid item xs={12} sm={6} md={4} key={workout.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">{workout.name}</Typography>
                    <Typography color="text.secondary" gutterBottom>
                      {new Date(workout.scheduledDate).toLocaleDateString()}
                    </Typography>
                    <Typography variant="body2">{workout.description}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
        </Grid>
      </TabPanel>

      {/* Embedded Google Calendar */}
      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <iframe
          src="https://calendar.google.com/calendar/embed?src=7799eb763a23aa9bf00de2b9daaafde472fd01069bd87770eb0c4f8b2637c1dd%40group.calendar.google.com&ctz=Asia%2FJerusalem"
          style={{ border: 0 }}
          width="800"
          height="600"
          frameBorder="0"
          scrolling="no"
          title="Gym Weekly Calendar"
        />
      </Box>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Workout</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Workout Name"
            fullWidth
            value={newWorkout.name || ''}
            onChange={(e) =>
              setNewWorkout({ ...newWorkout, name: e.target.value })
            }
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={4}
            value={newWorkout.description || ''}
            onChange={(e) =>
              setNewWorkout({ ...newWorkout, description: e.target.value })
            }
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Type</InputLabel>
            <Select
              value={newWorkout.type}
              label="Type"
              onChange={(e) =>
                setNewWorkout({
                  ...newWorkout,
                  type: e.target.value as Workout['type'],
                })
              }
            >
              <MenuItem value="AMRAP">AMRAP</MenuItem>
              <MenuItem value="FOR_TIME">For Time</MenuItem>
              <MenuItem value="EMOM">EMOM</MenuItem>
            </Select>
          </FormControl>
          <TextField
            margin="dense"
            label="Coach"
            fullWidth
            value={newWorkout.coach || ''}
            onChange={(e) =>
              setNewWorkout({ ...newWorkout, coach: e.target.value })
            }
          />
          <TextField
            margin="dense"
            label="Scheduled Date"
            type="datetime-local"
            fullWidth
            InputLabelProps={{ shrink: true }}
            value={newWorkout.scheduledDate || ''}
            onChange={(e) =>
              setNewWorkout({ ...newWorkout, scheduledDate: e.target.value })
            }
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateWorkout} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
} 