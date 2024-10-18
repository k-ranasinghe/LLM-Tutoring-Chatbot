import React, { useEffect, useState } from "react";
import {
    Container,
    Typography,
    Grid,
    Button,
    Box,
    TextField,
    CircularProgress,
    List,
    ListItem,
    ListItemText,
    ListItemSecondaryAction,
    IconButton,
} from "@mui/material";
import DeleteIcon from '@mui/icons-material/Delete';
import SideBar from '../components/SideBar.tsx';

const MentorQueries: React.FC = () => {
    const [queries, setQueries] = useState<any[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [mentorResponse, setMentorResponse] = useState<string>("");
    const [mentorId, setMentorId] = useState<string>("");
    const [selectedQueryId, setSelectedQueryId] = useState<string | null>(null);
    const [updating, setUpdating] = useState<boolean>(false);

    // Fetching user queries
    const fetchQueries = async () => {
        setLoading(true);
        try {
            const response = await fetch("http://127.0.0.1:8000/get-mentor-queries", {
                method: "POST",
            });
            if (!response.ok) throw new Error("Failed to fetch queries");
            const data = await response.json();
            console.log(data);

            // Transform the tuples into objects
            const transformedQueries = data.queries.map((query: any) => ({
                id: query[0],
                userId: query[1],
                queryText: query[2],
                chatbotResponse: query[3],
            }));

            setQueries(transformedQueries); // Set the transformed queries
        } catch (error) {
            console.error("Error fetching queries:", error);
            alert("Error fetching queries");
        } finally {
            setLoading(false);
        }
    };

    const handleResponseSubmit = async (queryId: string) => {
        if (!mentorResponse) return;
        console.log(queryId, mentorResponse, mentorId)
        setUpdating(true);
        try {
            const response = await fetch("http://127.0.0.1:8000/respond-to-query", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ queryId, mentorResponse, mentorId }),
            });

            if (!response.ok) throw new Error("Failed to submit response");

            alert("Response submitted successfully!");
            setMentorResponse("");
            setMentorId("");
            fetchQueries(); // Refresh the queries list after submitting
        } catch (error) {
            console.error("Error submitting response:", error);
            alert("Error submitting response");
        } finally {
            setUpdating(false);
        }
    };

    const handleDeleteQuery = async (queryId: string) => {
        const confirmDelete = window.confirm("Are you sure you want to delete this query?");
        if (!confirmDelete) return;

        try {
            const response = await fetch(`http://127.0.0.1:8000/delete-mentor_query?queryId=${queryId}`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                }
            });

            if (!response.ok) throw new Error("Failed to delete query");

            alert("Query deleted successfully!");
            fetchQueries(); // Refresh the queries list after deleting
        } catch (error) {
            console.error("Error deleting query:", error);
            alert("Error deleting query");
        }
    };

    const handleSelectQuery = (queryId: string) => {
        setSelectedQueryId(queryId);
    };

    useEffect(() => {
        fetchQueries();
    }, []);

    return (
        <Box sx={{ display: 'flex' }}>
            <SideBar />
            <Box sx={{ flexGrow: 1, padding: 3 }}>
                <style>
                    {`
                        ::-webkit-scrollbar {
                            width: 20px; /* Width of the scrollbar */
                            background: transparent; /* Transparent background */
                        }
                        ::-webkit-scrollbar-thumb {
                            background-color: rgba(90, 90, 90, 0.8); /* Lighter thumb color */
                            border-left: 4px solid #212121;
                            border-right: 4px solid #212121;
                        }
                        ::-webkit-scrollbar-thumb:hover {
                            background: rgba(90, 90, 90, 1); /* Darker thumb on hover */
                        }
                    `}
                </style>
                <Container sx={{ marginTop: "10vh", backgroundColor: "#171717", borderRadius: "8px", padding: 3 }}>
                    <Typography variant="h4" gutterBottom>
                        Mentor Queries
                    </Typography>
                    {loading ? (
                        <CircularProgress />
                    ) : (
                        <Grid container spacing={2}>
                            <Grid item xs={12}>
                                <List>
                                    {queries.map((query) => (
                                        <React.Fragment key={query.id}>
                                            <ListItem
                                                button
                                                onClick={() => handleSelectQuery(query.id)}
                                                sx={{
                                                    backgroundColor: selectedQueryId === query.id ? '#2f2f2f' : 'transparent',
                                                    transition: 'background-color 0.3s',
                                                    borderRadius: '4px',
                                                    '&:hover': {
                                                        backgroundColor: '#2f2f2f55',
                                                    },
                                                }}
                                            >
                                                <ListItemText
                                                    secondary={
                                                        <>
                                                            <Typography variant="caption" color="textSecondary">
                                                                User ID: {query.userId}
                                                            </Typography>
                                                            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>{query.queryText}</Typography>
                                                            <Typography variant="body2" color="textSecondary">
                                                                Chatbot Response: {query.chatbotResponse}
                                                            </Typography>
                                                        </>
                                                    }
                                                />
                                                <ListItemSecondaryAction>
                                                    <IconButton
                                                        edge="end"
                                                        aria-label="delete"
                                                        onClick={() => handleDeleteQuery(query.id)}
                                                        sx={{
                                                            '&:hover': {
                                                                color: 'red', // Change color to red on hover
                                                            },
                                                        }}
                                                    >
                                                        <DeleteIcon />
                                                    </IconButton>
                                                </ListItemSecondaryAction>
                                            </ListItem>

                                            {/* Conditionally render response panel below the selected query */}
                                            {selectedQueryId === query.id && (
                                                <Box mt={2} mb={2}>
                                                    <TextField
                                                        label="Mentor ID"
                                                        variant="outlined"
                                                        fullWidth
                                                        value={mentorId}
                                                        onChange={(e) => setMentorId(e.target.value)}
                                                        sx={{ marginBottom: 2 }} // Add some spacing
                                                    />
                                                    <TextField
                                                        label="Your Response"
                                                        variant="outlined"
                                                        fullWidth
                                                        multiline
                                                        rows={4}
                                                        value={mentorResponse}
                                                        onChange={(e) => setMentorResponse(e.target.value)}
                                                    />
                                                    <Button
                                                        variant="contained"
                                                        color="primary"
                                                        onClick={() => handleResponseSubmit(query.id)}
                                                        disabled={!mentorResponse || !mentorId || updating}
                                                        fullWidth
                                                        sx={{ marginTop: 2 }}
                                                    >
                                                        {updating ? <CircularProgress size={24} /> : "Submit Response"}
                                                    </Button>
                                                </Box>
                                            )}
                                        </React.Fragment>
                                    ))}
                                </List>
                            </Grid>
                        </Grid>
                    )}
                </Container>
            </Box>
        </Box>
    );
};

export default MentorQueries;
