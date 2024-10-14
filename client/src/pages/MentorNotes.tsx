import React, { useState } from "react";
import {
    Container,
    Typography,
    Grid,
    Button,
    Box,
    TextField,
    CircularProgress,
    FormControl,
    Radio,
    RadioGroup,
    FormControlLabel,
    Slider
} from "@mui/material";
import SideBar from '../components/SideBar.tsx';

const MentorNotes: React.FC = () => {
    const [uploading, setUploading] = useState<boolean>(false);
    const [weekNo, setWeekNo] = useState<number | string>("");
    const [hasAttended, setHasAttended] = useState<boolean>(false);
    const [activitySummary, setActivitySummary] = useState<string>("");
    const [communicationRating, setCommunicationRating] = useState<number | string>("");
    const [leadershipRating, setLeadershipRating] = useState<number | string>("");
    const [behaviourRating, setBehaviourRating] = useState<number | string>("");
    const [responsivenessRating, setResponsivenessRating] = useState<number | string>("");
    const [difficultConcepts, setDifficultConcepts] = useState<string>("");
    const [understoodConcepts, setUnderstoodConcepts] = useState<string>("");
    const [studentId, setStudentId] = useState<string>("");
    const [staffId, setStaffId] = useState<string>("");
    const [courseId, setCourseId] = useState<string>("");
    const [result, setResult] = useState<any>(null);

    // Function to handle slider changes
    const handleSliderChange = (setter) => (event, newValue) => {
        setter(newValue);
    };

    const handleFileUpload = async () => {
        if (!activitySummary || !weekNo || !studentId || !courseId) return;

        setUploading(true);

        // Create a timestamp in the desired format
        const now = new Date();
        const dateCreated = now.toISOString(); // This will give you "YYYY-MM-DDTHH:mm:ss.sssZ"
        // Remove the 'Z' and append microseconds
        const dateCreatedFormatted = dateCreated.replace('Z', '') + '000';

        const formData = new FormData();
        formData.append("week_no", String(weekNo));
        formData.append("has_attended", hasAttended ? 'true' : 'false')
        formData.append("activity_summary", activitySummary);
        formData.append("communication_rating", String(communicationRating));
        formData.append("leadership_rating", String(leadershipRating));
        formData.append("behaviour_rating", String(behaviourRating));
        formData.append("responsiveness_rating", String(responsivenessRating));
        formData.append("difficult_concepts", difficultConcepts);
        formData.append("understood_concepts", understoodConcepts);
        formData.append("student_id", studentId);
        formData.append("staff_id", staffId);
        formData.append("course_id", courseId);
        formData.append("date_created", dateCreatedFormatted);

        try {
            const response = await fetch(
                "http://127.0.0.1:8000/mentor-notes",
                {
                    method: "POST",
                    body: formData,
                }
            );

            if (!response.ok) {
                throw new Error("Note upload failed");
            }

            const result = await response.json();
            console.log(result);
            setResult(result);
            alert("Note submitted successfully!");
            setWeekNo("");
            setHasAttended(false);
            setActivitySummary("");
            setCommunicationRating("");
            setLeadershipRating("");
            setBehaviourRating("");
            setResponsivenessRating("");
            setDifficultConcepts("");
            setUnderstoodConcepts("");
            setStudentId("");
            setStaffId("");
            setCourseId("");

        } catch (error) {
            console.error("Error uploading Note:", error);
            alert("Error uploading Note");
        } finally {
            setUploading(false);
        }
    };

    return (
        <Box sx={{ display: 'flex' }}>  {/* Flex container for sidebar and content */}
            <SideBar />
            <Box sx={{ flexGrow: 1, padding: 3 }}>  {/* Content area with padding */}
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
                <Container sx={{ marginTop: "10vh" }}>
                    <Typography variant="h4" gutterBottom>
                        Submit Mentor Notes
                    </Typography>
                    <Box mt={2}>
                        <Grid container spacing={2}>
                            {/* Left Column for TextFields */}
                            <Grid item xs={8}>
                                <TextField
                                    label="Activity Summary"
                                    variant="outlined"
                                    fullWidth
                                    margin="normal"
                                    multiline
                                    rows={5}
                                    value={activitySummary}
                                    onChange={(e) => setActivitySummary(e.target.value)}
                                />
                                <TextField
                                    label="Difficult Concepts"
                                    variant="outlined"
                                    fullWidth
                                    margin="normal"
                                    multiline
                                    rows={3}
                                    value={difficultConcepts}
                                    onChange={(e) => setDifficultConcepts(e.target.value)}
                                />
                                <TextField
                                    label="Understood Concepts"
                                    variant="outlined"
                                    fullWidth
                                    margin="normal"
                                    multiline
                                    rows={3}
                                    value={understoodConcepts}
                                    onChange={(e) => setUnderstoodConcepts(e.target.value)}
                                />
                            </Grid>

                            {/* Right Column for Sliders */}
                            <Grid item xs={3} ml={6}>
                                <Grid container spacing={2} mb={2}>
                                    <Grid item xs={6}>
                                        <TextField
                                            label="Week Number"
                                            variant="outlined"
                                            fullWidth
                                            margin="normal"
                                            value={weekNo}
                                            onChange={(e) => setWeekNo(e.target.value)}
                                        />
                                    </Grid>
                                    <Grid item xs={4} ml={2} mt={-2}>
                                        <FormControl fullWidth margin="normal">
                                            <Box display="flex" alignItems="center">
                                                <RadioGroup
                                                    row
                                                    value={hasAttended ? "Yes" : "No"}
                                                    onChange={(e) => setHasAttended(e.target.value === "Yes")}
                                                    sx={{ display: 'flex', flexDirection: 'row' }}
                                                >
                                                    <FormControlLabel value="Yes" control={<Radio />} label="Present" />
                                                    <FormControlLabel value="No" control={<Radio />} label="Absent" />
                                                </RadioGroup>
                                            </Box>
                                        </FormControl>
                                    </Grid>
                                </Grid>
                                <Grid container spacing={2}>
                                    <Grid item xs={12}>
                                        <Typography gutterBottom>
                                            Communication Rating: {communicationRating}
                                        </Typography>
                                        <Slider
                                            value={communicationRating}
                                            onChange={handleSliderChange(setCommunicationRating)}
                                            min={0}
                                            max={10}
                                            step={1}
                                            valueLabelDisplay="auto"
                                        />
                                    </Grid>
                                    <Grid item xs={12}>
                                        <Typography gutterBottom>
                                            Leadership Rating: {leadershipRating}
                                        </Typography>
                                        <Slider
                                            value={leadershipRating}
                                            onChange={handleSliderChange(setLeadershipRating)}
                                            min={0}
                                            max={10}
                                            step={1}
                                            valueLabelDisplay="auto"
                                        />
                                    </Grid>
                                    <Grid item xs={12}>
                                        <Typography gutterBottom>
                                            Behaviour Rating: {behaviourRating}
                                        </Typography>
                                        <Slider
                                            value={behaviourRating}
                                            onChange={handleSliderChange(setBehaviourRating)}
                                            min={0}
                                            max={10}
                                            step={1}
                                            valueLabelDisplay="auto"
                                        />
                                    </Grid>
                                    <Grid item xs={12}>
                                        <Typography gutterBottom>
                                            Responsiveness Rating: {responsivenessRating}
                                        </Typography>
                                        <Slider
                                            value={responsivenessRating}
                                            onChange={handleSliderChange(setResponsivenessRating)}
                                            min={0}
                                            max={10}
                                            step={1}
                                            valueLabelDisplay="auto"
                                        />
                                    </Grid>
                                </Grid>
                            </Grid>
                        </Grid>

                        <Grid container spacing={2}>
                            <Grid item xs={4}>
                                <TextField
                                    label="Student ID"
                                    variant="outlined"
                                    fullWidth
                                    margin="normal"
                                    value={studentId}
                                    onChange={(e) => setStudentId(e.target.value)}
                                />
                            </Grid>
                            <Grid item xs={4}>
                                <TextField
                                    label="Staff ID"
                                    variant="outlined"
                                    fullWidth
                                    margin="normal"
                                    value={staffId}
                                    onChange={(e) => setStaffId(e.target.value)}
                                />
                            </Grid>
                            <Grid item xs={4}>
                                <TextField
                                    label="Course ID"
                                    variant="outlined"
                                    fullWidth
                                    margin="normal"
                                    value={courseId}
                                    onChange={(e) => setCourseId(e.target.value)}
                                />
                            </Grid>
                        </Grid>
                    </Box>

                    <Box mt={2}>
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={handleFileUpload}
                            disabled={!activitySummary || uploading || !weekNo || !studentId || !courseId}
                            fullWidth
                        >
                            {uploading ? <CircularProgress size={24} /> : "Submit"}
                        </Button>
                    </Box>
                    {/* Display result after submission */}
                    {result && (
                        <Box mt={4}>
                            <Typography variant="h6">Student Records</Typography>
                            <pre>{JSON.stringify(result, null, 2)}</pre>
                        </Box>
                    )}
                </Container>
            </Box>
        </Box>
    );
};

export default MentorNotes;
