// Map of AP courses to typical credit values at UVA
// Note: Actual credits may vary by score and department policy
export const AP_CREDIT_MAP: Record<string, number> = {
  'AP Research': 3,
  'AP Seminar': 3,
  'AP English Language and Composition': 3,
  'AP English Literature and Composition': 3,
  'AP Spanish Language and Culture': 6,
  'AP Spanish Literature and Culture': 6,
  'AP French Language and Culture': 6,
  'AP German Language and Culture': 6,
  'AP Italian Language and Culture': 6,
  'AP Chinese Language and Culture': 6,
  'AP Japanese Language and Culture': 6,
  'AP Latin': 6,
  'AP Environmental Science': 4,
  'AP Physics 1': 4,
  'AP Physics 2': 4,
  'AP Physics C: Mechanics': 4,
  'AP Physics C: Electricity and Magnetism': 4,
  'AP Chemistry': 4,
  'AP Biology': 8,
  'AP Computer Science Principles': 3,
  'AP Statistics': 3,
  'AP Calculus AB': 4,
  'AP Calculus BC': 8,
  'AP Precalculus': 3,
  'AP Computer Science A': 3,
  'AP World History: Modern': 3,
  'AP European History': 3,
  'AP Human Geography': 3,
  'AP African American Studies': 3,
  'AP US History': 3,
  'AP US Government and Politics': 3,
  'AP Comparative Government and Politics': 3,
  'AP Macroeconomics': 3,
  'AP Microeconomics': 3,
  'AP Psychology': 3,
  'AP 2D Art and Design': 3,
  'AP 3D Art and Design': 3,
  'AP Drawing': 3,
  'AP Art History': 3,
  'AP Music Theory': 3,
};

export function calculateAPCredits(apCourses: string[]): number {
  return apCourses.reduce((total, course) => {
    return total + (AP_CREDIT_MAP[course] || 0);
  }, 0);
}

export function isFirstYear(entryYear: number | null): boolean {
  if (!entryYear) return true;
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth();

  // Academic year starts in August (month 7)
  const academicYear = currentMonth >= 7 ? currentYear : currentYear - 1;

  return entryYear === academicYear;
}
