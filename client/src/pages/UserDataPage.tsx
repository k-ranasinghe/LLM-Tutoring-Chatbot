import React, { useEffect, useState } from "react";
import {
    Container,
    Typography,
    Grid,
    Box,
    CircularProgress,
    List,
    ListItem,
    ListItemText,
    Button,
    TextField,
} from "@mui/material";
import SideBar from '../components/SideBar.tsx';

const UserData: React.FC = () => {
    const [users, setUsers] = useState<any[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [searchStudent, setSearchStudent] = useState<string>("");
    const [searchMentor, setSearchMentor] = useState<string>("");

    // Fetching user data
    const fetchUsers = async () => {
        setLoading(true);
        try {
            const response = await fetch("http://127.0.0.1:8000/get-users", {
                method: "GET",
            });
            if (!response.ok) throw new Error("Failed to fetch user data");
            const data = await response.json();
            setUsers(data); // Set the fetched user data
        } catch (error) {
            console.error("Error fetching user data:", error);
            alert("Error fetching user data");
        } finally {
            setLoading(false);
        }
    };

    const handleRoleChange = async (userId: string, isAdmin: boolean) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/update-user`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ userId, isAdmin }),
            });

            if (!response.ok) throw new Error("Failed to update user role");
            alert("User role updated successfully!");
            fetchUsers(); // Refresh the user list after updating
        } catch (error) {
            console.error("Error updating user role:", error);
            alert("Error updating user role");
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    // Filtering for students
    const filteredStudents = users.filter(user => 
        !user.isAdmin && 
        (user.name?.toLowerCase().includes(searchStudent.toLowerCase()) || 
        user.UserID?.toString().includes(searchStudent))
    );

    // Filtering for mentors
    const filteredMentors = users.filter(user => 
        user.isAdmin && 
        (user.name?.toLowerCase().includes(searchMentor.toLowerCase()) || 
        user.UserID?.toString().includes(searchMentor))
    );

    return (
        <Box sx={{ display: 'flex' }}>
            <SideBar />
            <Box sx={{ flexGrow: 1, padding: 3 }}>
                <Container sx={{ marginTop: "10vh", backgroundColor: "#171717", borderRadius: "8px", padding: 3 }}>
                    <Typography variant="h4" gutterBottom>
                        User Management
                    </Typography>

                    {loading ? (
                        <CircularProgress />
                    ) : (
                        <Grid container spacing={2}>
                            <Grid item xs={12}>
                                <div className="bg-custombg p-2 py-4 rounded-2xl mb-10">
                                    <Typography variant="h5">Students</Typography>
                                    <TextField
                                        variant="outlined"
                                        placeholder="Search Students"
                                        value={searchStudent}
                                        onChange={(e) => setSearchStudent(e.target.value)}
                                        fullWidth
                                        margin="normal"
                                    />
                                    <Box sx={{ maxHeight: 200, overflowY: 'auto' }}>
                                        <List>
                                            {filteredStudents.slice(0, 5).map((user) => (
                                                <ListItem key={user.UserID} sx={{ borderRadius: '4px', '&:hover': { backgroundColor: '#4f4d4d' } }}>
                                                    <ListItemText
                                                        primary={<Typography variant="h6" sx={{ fontWeight: 'bold' }}>Name: {user.name}</Typography>}
                                                        secondary={
                                                            <>
                                                                <Typography variant="body2" color="textSecondary">
                                                                    <strong>User ID:</strong> {user.UserID}
                                                                </Typography>
                                                                <Typography variant="body2" color="textSecondary">
                                                                    <strong>Date of Birth:</strong> {new Date(user.Date_of_birth).toLocaleDateString()}
                                                                </Typography>
                                                                <Typography variant="body2" color="textSecondary">
                                                                    <strong>Phone Number:</strong> {user.phone_number}
                                                                </Typography>
                                                            </>
                                                        }
                                                    />
                                                    <Button variant="contained" color="primary" onClick={() => handleRoleChange(user.UserID, true)}>
                                                        Promote to Mentor
                                                    </Button>
                                                </ListItem>
                                            ))}
                                        </List>
                                    </Box>
                                </div>

                                <div className="bg-custombg p-2 py-4 rounded-2xl">
                                    <Typography variant="h5" sx={{ marginTop: 4 }}>Mentors</Typography>
                                    <TextField
                                        variant="outlined"
                                        placeholder="Search Mentors"
                                        value={searchMentor}
                                        onChange={(e) => setSearchMentor(e.target.value)}
                                        fullWidth
                                        margin="normal"
                                    />
                                    <Box sx={{ maxHeight: 200, overflowY: 'auto' }}>
                                        <List>
                                            {filteredMentors.slice(0, 5).map((user) => (
                                                <ListItem key={user.UserID} sx={{ borderRadius: '4px', '&:hover': { backgroundColor: '#4f4d4d' } }}>
                                                    <ListItemText
                                                        primary={<Typography variant="h6" sx={{ fontWeight: 'bold' }}>Name: {user.name}</Typography>}
                                                        secondary={
                                                            <>
                                                                <Typography variant="body2" color="textSecondary">
                                                                    <strong>User ID:</strong> {user.UserID}
                                                                </Typography>
                                                                <Typography variant="body2" color="textSecondary">
                                                                    <strong>Date of Birth:</strong> {new Date(user.Date_of_birth).toLocaleDateString()}
                                                                </Typography>
                                                                <Typography variant="body2" color="textSecondary">
                                                                    <strong>Phone Number:</strong> {user.phone_number}
                                                                </Typography>
                                                            </>
                                                        }
                                                    />
                                                    <Button variant="contained" color="secondary" onClick={() => handleRoleChange(user.UserID, false)}>
                                                        Demote to Student
                                                    </Button>
                                                </ListItem>
                                            ))}
                                        </List>
                                    </Box>
                                </div>
                            </Grid>
                        </Grid>
                    )}
                </Container>
            </Box>
        </Box>
    );
};

export default UserData;
