import React, { useState } from "react";
import {
    Container,
    Typography,
    Grid,
    Button,
    Box,
    TextField,
    CircularProgress,
    IconButton,
    Tooltip,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import DeleteIcon from "@mui/icons-material/Delete";

const MentorNotes: React.FC = () => {
    const [files, setFiles] = useState<File[]>([]);
    const [uploading, setUploading] = useState<boolean>(false);
    const [description, setDescription] = useState<string>("");
    const [mentorName, setMentorName] = useState<string>("");
    const [studentName, setStudentName] = useState<string>("");
    const [course, setCourse] = useState<string>("");
    const [combinedText, setCombinedText] = useState<string>("");
    const [mentorId, setMentorId] = useState<string>("");
    const [studentId, setStudentId] = useState<string>("");
    const [courseName, setCourseName] = useState<string>("");

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files) {
            setFiles([...files, ...Array.from(event.target.files)]);
        }
    };

    const handleFileRemove = (index: number) => {
        const updatedFiles = files.filter((_, i) => i !== index);
        setFiles(updatedFiles);
    };

    const handleFileUpload = async () => {
        if ((!files.length && !description) || !mentorName || !studentName || !course) return;

        setUploading(true);

        const formData = new FormData();
        files.forEach((file) => {
            formData.append("files", file);
        });
        formData.append("notes", description);
        formData.append("mentorid", mentorName);
        formData.append("studentid", studentName);
        formData.append("course", course);

        try {
            const response = await fetch(
                "http://127.0.0.1:8000/api/material/notes/",
                {
                    method: "POST",
                    body: formData,
                }
            );

            if (!response.ok) {
                throw new Error("File upload failed");
            }

            const result = await response.json();
            console.log(result);
            alert("Files submitted successfully!");
            setFiles([]);
            setDescription("");
            setMentorName("");
            setStudentName("");
            setCourse("");

            setCombinedText(result.combined_text);
            setMentorId(result.mentor_id);
            setStudentId(result.student_id);
            setCourseName(result.course);

        } catch (error) {
            console.error("Error uploading files:", error);
            alert("Error uploading files");
        } finally {
            setUploading(false);
        }
    };

    return (
        <Container sx={{ marginTop: "10vh" }}>
            <Typography variant="h4" gutterBottom>
                Submit Mentor Notes
            </Typography>
            <Box mt={4} p={3} border={1} borderRadius="8px" bgcolor="#f9f9f9">
                <Typography variant="h5" gutterBottom>
                    Supported File Formats
                </Typography>

                <Box mb={3}>
                    <Typography variant="body1" paragraph style={{ marginBottom: '0px' }}>
                        Our platform supports a wide range of text and image file formats, ensuring ease of use for the mentors:
                    </Typography>
                    <Typography variant="body1" paragraph>
                        <Tooltip title='Portable Document Format' arrow><strong style={{ marginRight: '20px' }}>.pdf</strong></Tooltip>
                        <Tooltip title='Microsoft Word' arrow><strong style={{ marginRight: '20px' }}>.docs</strong></Tooltip>
                        <Tooltip title='Plain Text File' arrow><strong style={{ marginRight: '20px' }}>.txt</strong></Tooltip>
                        <Tooltip title='Portable Network Graphics' arrow><strong style={{ marginRight: '20px' }}>.png</strong></Tooltip>
                        <Tooltip title='JPEG Image' arrow><strong style={{ marginRight: '20px' }}>.jpg</strong></Tooltip>
                        <Tooltip title='JPEG Image' arrow><strong style={{ marginRight: '20px' }}>.jpeg</strong></Tooltip>
                        <Tooltip title='Bitmap Image File' arrow><strong style={{ marginRight: '20px' }}>.bmp</strong></Tooltip>
                        <Tooltip title='Tagged Image File Format' arrow><strong style={{ marginRight: '20px' }}>.tiff</strong></Tooltip>
                        <Tooltip title='WebP Image' arrow><strong style={{ marginRight: '20px' }}>.webp</strong></Tooltip>
                    </Typography>
                    <Typography variant="body1" paragraph style={{ marginTop: '20px' }}>
                        Attaching a file is not necessary if you can provide the information in the "description" text area.
                    </Typography>
                </Box>
            </Box>
            <Grid container spacing={2} style={{ marginTop: "20px" }}>
                <Grid item xs={12}>
                    <Button
                        variant="contained"
                        component="label"
                        startIcon={<CloudUploadIcon />}
                        fullWidth
                    >
                        Select Files
                        <input
                            type="file"
                            hidden
                            multiple
                            onChange={handleFileChange}
                            accept=".pdf,.docx,.txt,.png,.jpg,.jpeg,.bmp,.tiff,.webp"
                        />
                    </Button>
                </Grid>
            </Grid>
            <Box mt={2}>
                {files.length > 0 && (
                    <Box mt={2}>
                        <Typography variant="h6">Selected Files</Typography>
                        {files.map((file, index) => (
                            <Box
                                key={index}
                                display="flex"
                                alignItems="center"
                                justifyContent="space-between"
                                border={1}
                                borderRadius={1}
                                p={2}
                                borderColor="grey.400"
                                mb={1}
                            >
                                <Typography>{file.name}</Typography>
                                <IconButton
                                    color="error"
                                    onClick={() => handleFileRemove(index)}
                                >
                                    <DeleteIcon />
                                </IconButton>
                            </Box>
                        ))}
                    </Box>
                )}
            </Box>

            <Box mt={2}>
                <TextField
                    label="Description"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    multiline
                    rows={4}
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                />
                <TextField
                    label="Mentor ID"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    value={mentorName}
                    onChange={(e) => setMentorName(e.target.value)}
                />
                <TextField
                    label="Student ID"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    value={studentName}
                    onChange={(e) => setStudentName(e.target.value)}
                />
                <FormControl fullWidth variant="outlined" margin="normal" size="small">
                    <InputLabel>Course</InputLabel>
                    <Select
                        value={course}
                        onChange={(e) => setCourse(e.target.value as string)}
                        label="Course"
                        style={{ fontSize: '1.1rem' }}
                    >
                        <MenuItem value="">Select a course</MenuItem>
                        <MenuItem value="Programming & Electronics">Programming</MenuItem>
                        <MenuItem value="Programming & Electronics">Electronics</MenuItem>
                        <MenuItem value="3D Design & Manufacturing">3D Design</MenuItem>
                        <MenuItem value="3D Design & Manufacturing">Manufacturing</MenuItem>
                    </Select>
                </FormControl>
            </Box>

            <Box mt={2}>
                <Button
                    variant="contained"
                    color="primary"
                    onClick={handleFileUpload}
                    disabled={(!files.length && !description) || uploading || !mentorName || !studentName || !course}
                    fullWidth
                >
                    {uploading ? <CircularProgress size={24} /> : "Submit"}
                </Button>
            </Box>
            {combinedText && (
                <Box mt={4}>
                    <Typography variant="h6">Updated Notes</Typography>
                    <Typography variant="body1">Mentor ID: {mentorId}</Typography>
                    <Typography variant="body1">Student ID: {studentId}</Typography>
                    <Typography variant="body1">Course: {courseName}</Typography>
                    <Typography variant="body1" mt={2}>{combinedText}</Typography>
                </Box>
            )}
        </Container>
    );
};

export default MentorNotes;
