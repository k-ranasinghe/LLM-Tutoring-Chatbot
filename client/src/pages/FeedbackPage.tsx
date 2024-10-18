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
    IconButton,
    TextField,
    Button,
    Checkbox,
} from "@mui/material";
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import CloseIcon from '@mui/icons-material/Close';
import SideBar from '../components/SideBar.tsx';

const FeedbackLogs: React.FC = () => {
    const [feedbackLogs, setFeedbackLogs] = useState<any[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [selectedLogId, setSelectedLogId] = useState<string | null>(null);
    const [editingLogId, setEditingLogId] = useState<string | null>(null);
    const [editedInstruction, setEditedInstruction] = useState<string>("");

    // Fetching feedback logs
    const fetchFeedbackLogs = async () => {
        setLoading(true);
        try {
            const response = await fetch("http://127.0.0.1:8000/feedback-logs", {
                method: "GET",
            });
            if (!response.ok) throw new Error("Failed to fetch feedback logs");
            const data = await response.json();
            setFeedbackLogs(data);
        } catch (error) {
            console.error("Error fetching feedback logs:", error);
            alert("Error fetching feedback logs");
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteLog = async (logId: number) => {
        const confirmDelete = window.confirm("Are you sure you want to delete this feedback log?");
        if (!confirmDelete) return;

        try {
            const response = await fetch(`http://127.0.0.1:8000/delete-feedback?id=${logId}`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                }
            });

            if (!response.ok) throw new Error("Failed to delete feedback log");

            alert("Feedback log deleted successfully!");
            fetchFeedbackLogs();
        } catch (error) {
            console.error("Error deleting feedback log:", error);
            alert("Error deleting feedback log");
        }
    };

    const handleToggleLog = (logId: string) => {
        setSelectedLogId(selectedLogId === logId ? null : logId);
    };

    const handleEditClick = (log: any) => {
        setEditingLogId(log.id);
        setEditedInstruction(log.instruction);
    };

    const handleSaveEdit = async (logId: number, currentSelection: boolean) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/update-feedback`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ id: logId, instruction: editedInstruction, selected: currentSelection }),
            });

            if (!response.ok) throw new Error("Failed to update feedback log");

            alert("Feedback log updated successfully!");
            setEditingLogId(null);
            fetchFeedbackLogs();
        } catch (error) {
            console.error("Error updating feedback log:", error);
            alert("Error updating feedback log");
        }
    };

    const handleCancelEdit = () => {
        setEditingLogId(null);
        setEditedInstruction("");
    };

    const handleCheckboxChange = async (logId: number, instruction: string, currentSelection: boolean) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/update-feedback`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ id: logId, instruction: instruction, selected: !currentSelection }), // Toggle selected state
            });

            if (!response.ok) throw new Error("Failed to update selection");

            fetchFeedbackLogs(); // Refresh the feedback logs list
        } catch (error) {
            console.error("Error updating feedback selection:", error);
            alert("Error updating feedback selection");
        }
    };

    useEffect(() => {
        fetchFeedbackLogs();
    }, []);

    return (
        <Box sx={{ display: 'flex' }}>
            <SideBar />
            <Box sx={{ flexGrow: 1, padding: 3 }}>
                <Container sx={{ marginTop: "10vh", backgroundColor: "#171717", borderRadius: "8px", padding: 3 }}>
                    <Typography variant="h4" gutterBottom>
                        Feedback Logs
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                        Given below are the feedback logs received from the users for the chatbot responses. 
                        Once the user provides feedback, a instruction is generated internally which is given 
                        to the model in the future to improve the responses. You can edit the instruction and
                        select the logs to be used for training the model by checking the checkbox. You can also
                        delete the logs if they are not useful.
                    </Typography>
                    {loading ? (
                        <CircularProgress />
                    ) : (
                        <Grid container spacing={2}>
                            <Grid item xs={12}>
                                <List>
                                    {feedbackLogs.map((log) => (
                                        <React.Fragment key={log.id}>
                                            <ListItem 
                                                button 
                                                onClick={() => handleToggleLog(log.id)} 
                                                sx={{ borderRadius: '4px', '&:hover': { backgroundColor: '#2f2f2f55' } }}
                                            >
                                                <Checkbox
                                                    checked={log.selected === 1}
                                                    onChange={() => handleCheckboxChange(log.id, log.instruction, log.selected === 1)}
                                                />
                                                <ListItemText
                                                    primary={
                                                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                                                            <span style={{ fontWeight: 'bold' }}>Feedback Type: </span>
                                                            <span style={{ color: log.feedback_type === 'positive' ? '#008000c7' : '#ff000085', fontWeight: 'bold' }}>
                                                                {log.feedback_type}
                                                            </span>
                                                        </Typography>
                                                    }
                                                    secondary={
                                                        <>
                                                            {editingLogId === log.id ? (
                                                                <TextField
                                                                    variant="outlined"
                                                                    value={editedInstruction}
                                                                    onChange={(e) => setEditedInstruction(e.target.value)}
                                                                    fullWidth
                                                                    margin="normal"
                                                                    multiline
                                                                    rows={5}
                                                                    sx={{ marginBottom: 1 }}
                                                                />
                                                            ) : (
                                                                <Typography variant="body2" color="textSecondary" marginBottom={1}>
                                                                    <span style={{ fontWeight: 'bold', color: '#757958c7' }}>Instruction: </span>{log.instruction}
                                                                </Typography>
                                                            )}
                                                            {selectedLogId === log.id && (
                                                                <>
                                                                <Typography variant="body2" color="textSecondary" marginBottom={1}>
                                                                    <span style={{ fontWeight: 'bold', color: '#757958c7' }}>User ID: </span>{log.userid}
                                                                </Typography>
                                                                <Typography variant="body2" color="textSecondary" marginBottom={1}>
                                                                    <span style={{ fontWeight: 'bold', color: '#757958c7' }}>Query: </span>{log.user_query}
                                                                </Typography>
                                                                <Typography variant="body2" color="textSecondary" marginBottom={1}>
                                                                    <span style={{ fontWeight: 'bold', color: '#757958c7' }}>Response: </span>{log.response}
                                                                </Typography>
                                                                <Typography variant="body2" color="textSecondary" marginBottom={1}>
                                                                    <span style={{ fontWeight: 'bold', color: '#757958c7' }}>Feedback Text: </span>{log.feedback_text}
                                                                </Typography>
                                                                <Typography variant="body2" color="textSecondary" marginBottom={1}>
                                                                    <span style={{ fontWeight: 'bold', color: '#757958c7' }}>Created At: </span>{new Date(log.created_at).toLocaleString()}
                                                                </Typography>
                                                                </>
                                                            )}
                                                        </>
                                                    }
                                                />
                                                {editingLogId === log.id ? (
                                                    <>
                                                        <IconButton
                                                            edge="end"
                                                            aria-label="cancel"
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                handleCancelEdit();
                                                            }}
                                                            sx={{
                                                                '&:hover': {
                                                                    color: 'red',
                                                                    backgroundColor: 'transparent',
                                                                },
                                                            }}
                                                        >
                                                            <CloseIcon />
                                                        </IconButton>
                                                        <IconButton
                                                            edge="end"
                                                            aria-label="save"
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                handleSaveEdit(log.id, log.selected);
                                                            }}
                                                            sx={{
                                                                '&:hover': {
                                                                    color: 'green',
                                                                    backgroundColor: 'transparent',
                                                                },
                                                            }}
                                                        >
                                                            <Button variant="contained" color="primary">Save</Button>
                                                        </IconButton>
                                                    </>
                                                ) : (
                                                    <IconButton
                                                        edge="end"
                                                        aria-label="edit"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            handleEditClick(log);
                                                        }}
                                                        sx={{
                                                            '&:hover': {
                                                                color: 'blue',
                                                                backgroundColor: 'transparent',
                                                            },
                                                        }}
                                                    >
                                                        <EditIcon />
                                                    </IconButton>
                                                )}
                                                <IconButton
                                                    edge="end"
                                                    aria-label="delete"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleDeleteLog(log.id);
                                                    }}
                                                    sx={{
                                                        '&:hover': {
                                                            color: 'red',
                                                            backgroundColor: 'transparent',
                                                        },
                                                    }}
                                                >
                                                    <DeleteIcon />
                                                </IconButton>
                                            </ListItem>
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

export default FeedbackLogs;
