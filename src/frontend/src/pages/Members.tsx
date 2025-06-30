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
  IconButton,
  Chip,
  Avatar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';

interface Member {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  membershipType: 'BASIC' | 'PREMIUM' | 'UNLIMITED';
  memberSince: string;
  lastCheckIn: string;
  status: 'ACTIVE' | 'INACTIVE' | 'PENDING';
}

export default function Members() {
  const [open, setOpen] = useState(false);
  const [editMember, setEditMember] = useState<Partial<Member> | null>(null);

  const queryClient = useQueryClient();

  const { data: members, isLoading } = useQuery<Member[]>({
    queryKey: ['members'],
    queryFn: () => api.get('/members').then((res) => res.data),
  });

  const createMemberMutation = useMutation({
    mutationFn: (member: Partial<Member>) =>
      api.post('/members', member).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['members'] });
      handleClose();
    },
  });

  const updateMemberMutation = useMutation({
    mutationFn: (member: Partial<Member>) =>
      api.put(`/members/${member.id}`, member).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['members'] });
      handleClose();
    },
  });

  const deleteMemberMutation = useMutation({
    mutationFn: (id: string) =>
      api.delete(`/members/${id}`).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['members'] });
    },
  });

  const handleClose = () => {
    setOpen(false);
    setEditMember(null);
  };

  const handleSave = () => {
    if (editMember?.id) {
      updateMemberMutation.mutate(editMember);
    } else {
      createMemberMutation.mutate(editMember!);
    }
  };

  const getStatusColor = (status: Member['status']) => {
    switch (status) {
      case 'ACTIVE':
        return 'success';
      case 'INACTIVE':
        return 'error';
      case 'PENDING':
        return 'warning';
      default:
        return 'default';
    }
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Members</Typography>
        <Button
          variant="contained"
          onClick={() => {
            setEditMember({});
            setOpen(true);
          }}
        >
          Add Member
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Membership</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Last Check-in</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {members?.map((member) => (
              <TableRow key={member.id}>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Avatar>
                      {member.firstName[0]}
                      {member.lastName[0]}
                    </Avatar>
                    <Typography>
                      {member.firstName} {member.lastName}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>{member.email}</TableCell>
                <TableCell>
                  <Chip label={member.membershipType} />
                </TableCell>
                <TableCell>
                  <Chip
                    label={member.status}
                    color={getStatusColor(member.status)}
                  />
                </TableCell>
                <TableCell>
                  {new Date(member.lastCheckIn).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <IconButton
                    onClick={() => {
                      setEditMember(member);
                      setOpen(true);
                    }}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    onClick={() => {
                      if (
                        window.confirm(
                          'Are you sure you want to delete this member?'
                        )
                      ) {
                        deleteMemberMutation.mutate(member.id);
                      }
                    }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editMember?.id ? 'Edit Member' : 'Add New Member'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={6}>
              <TextField
                label="First Name"
                fullWidth
                value={editMember?.firstName || ''}
                onChange={(e) =>
                  setEditMember({ ...editMember, firstName: e.target.value })
                }
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                label="Last Name"
                fullWidth
                value={editMember?.lastName || ''}
                onChange={(e) =>
                  setEditMember({ ...editMember, lastName: e.target.value })
                }
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Email"
                fullWidth
                type="email"
                value={editMember?.email || ''}
                onChange={(e) =>
                  setEditMember({ ...editMember, email: e.target.value })
                }
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Phone"
                fullWidth
                value={editMember?.phone || ''}
                onChange={(e) =>
                  setEditMember({ ...editMember, phone: e.target.value })
                }
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSave} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
} 