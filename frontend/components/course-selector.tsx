

export default function CourseSelector() {
  return (
    <label>
      Pick a Course:
      <select name="selectedCourse" defaultValue="All Courses">
        <option value="">All Courses</option>
        <option value="Theory of Numbers">Theory of Numbers</option>
        <option value="Course 2">Course 2</option>
        <option value="Course 3">Course 3</option>
      </select>
    </label>
  );
}
