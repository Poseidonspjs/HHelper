'use client';

import { useState, useEffect, useRef, useMemo } from 'react';
import { useRouter } from 'next/navigation';

type DropdownProps = {
  label: string;
  value: string | string[];
  onChange: (value: string | string[]) => void;
  options: string[];
  multiple?: boolean;
  placeholder?: string;
  error?: string;
  disabled?: boolean;
};

function Dropdown({
  label,
  value,
  onChange,
  options,
  multiple = false,
  placeholder = "Select an option",
  error,
  disabled = false,
}: DropdownProps) {
  const [open, setOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState(""); // State for search term
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const isMulti = Array.isArray(value);
  const filteredOptions = options.filter((opt) =>
    opt.toLowerCase().includes(searchTerm.toLowerCase()) // Filter options based on search term
  );

  return (
    <div className="text-gray-700 relative" ref={dropdownRef}>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>

      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={`w-full text-left flex justify-between items-center p-3 border rounded-lg bg-white text-gray-900 hover:ring-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
          error ? "border-red-500 hover:ring-red-500" : "border-gray-300 hover:ring-gray-300"
        }`}
      >
        <span
          className={`truncate ${
            (isMulti && (value as string[]).length === 0) ||
            (!isMulti && !value)
              ? "text-gray-400"
              : "text-gray-900"
          }`}
        >
          {isMulti
            ? (value as string[]).length > 0
              ? (value as string[]).join(", ")
              : placeholder
            : value || placeholder}
        </span>
        <svg
          className={`w-4 h-4 ml-2 text-gray-500 transition-transform duration-300 ${
            open ? "rotate-180" : "rotate-0"
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {open && (
        <div
          className="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto p-2 animate-bounce-soft"
        >
          {/* Search Input */}
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search..."
            className="w-full p-2 mb-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          />

          {filteredOptions.map((opt) => (
            <label
              key={opt}
              className={`flex items-center space-x-2 p-1 cursor-pointer ${
                multiple ? "hover:bg-gray-100 rounded" : ""
              }`}
            >
              {multiple ? (
                <input
                  type="checkbox"
                  value={opt}
                  checked={(value as string[]).includes(opt)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      onChange([...(value as string[]), opt]);
                    } else {
                      onChange(
                        (value as string[]).filter((v) => v !== opt)
                      );
                    }
                  }}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              ) : (
                <input
                  type="radio"
                  name={label}
                  value={opt}
                  checked={value === opt}
                  onChange={() => {
                    onChange(opt);
                    setOpen(false); // close after selecting
                  }}
                  className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                />
              )}
              <span className="text-sm text-gray-700">{opt}</span>
            </label>
          ))}

          {filteredOptions.length === 0 && (
            <p className="text-sm text-gray-500 text-center">No options found</p>
          )}
        </div>
      )}

      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  );
}

interface FormData {
  school: string;
  major: string;
  focusArea: string;
  entryYear: string;
  apCredits: string[];
  additionalDetails: string;
  transcript?: File | null;
  gpa?: string;
  creditsCompleted?: string;
}

interface FormErrors {
  school?: string;
  major?: string;
  focusArea?: string;
  entryYear?: string;
  apCredits?: string;
  transcript?: string;
}

export default function Home() {
  const router = useRouter();
  const [formData, setFormData] = useState<FormData>({
    school: '',
    major: "",
    focusArea: "",
    entryYear: "",
    apCredits: [],
    additionalDetails: "",
    transcript: null,
    gpa: "",
    creditsCompleted: "",
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [submitMessage, setSubmitMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);

  const [typedTagline, setTypedTagline] = useState(""); // For the main tagline
  const [typedSubtitle, setTypedSubtitle] = useState(""); // For the current subtitle
  const [animationPhase, setAnimationPhase] = useState<
    "typing-tagline" | "waiting-for-subtitle-start" | "typing-subtitle" | "deleting-subtitle"
  >("typing-tagline");
  const [currentSubtitleIndex, setCurrentSubtitleIndex] = useState(0);

  const tagline = useMemo(() => "Your UVA Course Planning Assistant", []);
  const subtitles = useMemo(() => [
    "Get Help With Your 4 Year Academic Plan",
    "Craft Your Ideal UVA Journey",
    "Get Personalized Course Recommendations",
    "Navigate Your Degree Requirements",
    "Optimize Your Course Load",
    "Plan for Study Abroad and Internships",
    "Maximize Your UVA Experience"
  ], []);
  const typingSpeed = 80;
  const deletingSpeed = 50;
  const pauseTimeAfterTagline = 1500; // Pause after main tagline is typed
  const pauseTimeAfterSubtitle = 1000; // Pause after subtitle is typed

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    const handleAnimation = () => {
      switch (animationPhase) {
        case "typing-tagline": // Types the main tagline once
          if (typedTagline.length < tagline.length) {
            setTypedTagline(tagline.slice(0, typedTagline.length + 1));
          } else {
            timeoutId = setTimeout(() => setAnimationPhase("waiting-for-subtitle-start"), pauseTimeAfterTagline);
          }
          break;

        case "waiting-for-subtitle-start": // Brief pause before first subtitle starts
          setAnimationPhase("typing-subtitle");
          break;

        case "typing-subtitle": // Types the current subtitle
          const currentSubtitle = subtitles[currentSubtitleIndex];
          if (typedSubtitle.length < currentSubtitle.length) {
            setTypedSubtitle(currentSubtitle.slice(0, typedSubtitle.length + 1));
          } else {
            timeoutId = setTimeout(() => setAnimationPhase("deleting-subtitle"), pauseTimeAfterSubtitle);
          }
          break;

        case "deleting-subtitle": // Deletes the current subtitle
          if (typedSubtitle.length > 0) {
            setTypedSubtitle(typedSubtitle.slice(0, typedSubtitle.length - 1));
          } else {
            // Subtitle deleted, move to next one
            setCurrentSubtitleIndex((prevIndex) => (prevIndex + 1) % subtitles.length);
            setAnimationPhase("typing-subtitle"); // Start typing the next subtitle
          }
          break;
      }
    }

    const speed = animationPhase.includes("deleting") ? deletingSpeed : typingSpeed;
    if (animationPhase === "waiting-for-subtitle-start") {
        timeoutId = setTimeout(handleAnimation, 0); // Immediate transition
    } else {
        timeoutId = setTimeout(handleAnimation, speed);
    }

    return () => clearTimeout(timeoutId);
  }, [typedTagline, typedSubtitle, animationPhase, currentSubtitleIndex, tagline, subtitles]);

  // Sample data - in a real app, these would come from API endpoints
  const school = [
    'School of Engineering and Applied Science',
    'McIntire School of Commerce',
    'College of Arts & Sciences',
    'School of Architecture',
    'School of Nursing',
    'School of Education and Human Development',
    'Frank Batten School of Leadership and Public Policy',
    'School of Data Science',
    'School of Continuing and Professional Studies'
  ]

  const majors = [
    'Aerospace Engineering',
    'African American and African Studies',
    'American Sign Language',
    'American Studies',
    'Anthropology',
    'Applied Mathematics',
    'Archaeology',
    'Architectural History',
    'Architecture',
    'Art History',
    'Asian Pacific American Studies',
    'Astronomy',
    'Behavioral Neuroscience',
    'Biology',
    'Biomedical Engineering',
    'Chemical Engineering',
    'Chemistry',
    'Chinese Language & Literature',
    'Civil Engineering',
    'Classics',
    'Cognitive Science',
    'Commerce',
    'Computer Engineering',
    'Computer Science',
    'Dance',
    'Data Analytics',
    'Data Science',
    'Drama',
    'Early Childhood Education',
    'East Asian Languages, Literatures and Culture',
    'Economics',
    'Electrical Engineering',
    'Elementary Education',
    'Engineering Science',
    'English',
    'Entrepreneurship',
    'Environmental Sciences',
    'Environmental Thought and Practice',
    'French',
    'German',
    'Global Culture and Commerce',
    'Global Studies',
    'Global Environments and Sustainability',
    'Health, Ethics, and Society',
    'Health Sciences Management',
    'History',
    'History of Art',
    'History of Science and Technology',
    'Human Biology',
    'Interdisciplinary Studies',
    'Italian',
    'Japanese Language & Literature',
    'Jewish Studies',
    'Kinesiology',
    'Korean',
    'Latin American Studies',
    'Leadership',
    'Linguistics',
    'Materials Science and Engineering',
    'Mathematics',
    'Mechanical Engineering',
    'Media Studies',
    'Medieval Studies',
    'Middle Eastern and South Asian Languages and Cultures',
    'Music',
    'Neuroscience',
    'Nursing',
    'Philosophy',
    'Physics',
    'Political and Social Thought',
    'Political Philosophy, Policy, and Law',
    'Politics',
    'Portuguese',
    'Psychology',
    'Public Policy and Leadership',
    'Religious Studies',
    'Slavic Languages and Literatures',
    'Sociology',
    'South Asian Languages and Literatures',
    'Spanish',
    'Special Education',
    'Speech Communication Disorders',
    'Statistics',
    'Studio Art',
    'Systems Engineering',
    'Urban and Environmental Planning',
    'Women, Gender & Sexuality',
    'Youth & Social Innovation'
  ];

  const focusAreas: Record<string, string[]> = {
    'Aerospace Engineering': ['Aerodynamics', 'Propulsion Systems', 'Space Systems', 'Flight Mechanics'],
    'African American and African Studies': ['History & Culture', 'Social Justice', 'Literature', 'Politics'],
    'American Sign Language': ['Interpretation', 'Deaf Culture', 'Language Structure', 'Education'],
    'American Studies': ['Cultural Studies', 'History', 'Politics', 'Literature'],
    'Anthropology': ['Cultural Anthropology', 'Archaeology', 'Biological Anthropology', 'Linguistic Anthropology'],
    'Applied Mathematics': ['Computational Math', 'Optimization', 'Mathematical Modeling', 'Data Analysis'],
    'Archaeology': ['Field Methods', 'Cultural Heritage', 'Material Culture', 'Bioarchaeology'],
    'Architectural History': ['Historic Preservation', 'Theory & Criticism', 'Urban History', 'Architectural Conservation'],
    'Architecture': ['Sustainable Design', 'Urban Design', 'Digital Fabrication', 'Historic Preservation'],
    'Art History': ['Renaissance', 'Modern & Contemporary', 'Museum Studies', 'Global Art'],
    'Asian Pacific American Studies': ['Migration & Diaspora', 'Cultural Identity', 'Social Justice', 'Literature'],
    'Astronomy': ['Astrophysics', 'Planetary Science', 'Cosmology', 'Observational Astronomy'],
    'Behavioral Neuroscience': ['Cognitive Neuroscience', 'Neuropsychology', 'Research Methods', 'Clinical Applications'],
    'Biology': ['Pre-Med', 'Research', 'Environmental Biology', 'Molecular Biology', 'Ecology'],
    'Biomedical Engineering': ['Medical Devices', 'Tissue Engineering', 'Biomechanics', 'Bioimaging'],
    'Chemical Engineering': ['Process Engineering', 'Materials', 'Biotechnology', 'Energy'],
    'Chemistry': ['Organic Chemistry', 'Physical Chemistry', 'Biochemistry', 'Analytical Chemistry'],
    'Chinese Language & Literature': ['Language Acquisition', 'Chinese Literature', 'Translation', 'Cultural Studies'],
    'Civil Engineering': ['Structural Engineering', 'Transportation', 'Environmental Engineering', 'Geotechnical'],
    'Classics': ['Greek & Roman History', 'Classical Languages', 'Archaeology', 'Ancient Philosophy'],
    'Cognitive Science': ['Neuroscience', 'AI & Machine Learning', 'Psychology', 'Linguistics'],
    'Commerce': ['Finance', 'Marketing', 'Management', 'Accounting', 'Information Technology'],
    'Computer Engineering': ['Embedded Systems', 'Computer Architecture', 'Networking', 'Robotics'],
    'Computer Science': ['Software Development', 'Data Science', 'Cybersecurity', 'AI/Machine Learning', 'Systems'],
    'Dance': ['Performance', 'Choreography', 'Dance History', 'Movement Studies'],
    'Data Analytics': ['Business Intelligence', 'Statistical Analysis', 'Machine Learning', 'Visualization'],
    'Data Science': ['Machine Learning', 'Statistical Modeling', 'Big Data', 'Data Visualization'],
    'Drama': ['Acting', 'Directing', 'Playwriting', 'Technical Theater'],
    'Early Childhood Education': ['Child Development', 'Curriculum Design', 'Special Needs', 'Family Engagement'],
    'East Asian Languages, Literatures and Culture': ['Language Studies', 'Literature', 'Cultural Studies', 'Translation'],
    'Economics': ['Public Policy', 'Finance', 'International Economics', 'Behavioral Economics'],
    'Electrical Engineering': ['Power Systems', 'Electronics', 'Control Systems', 'Signal Processing'],
    'Elementary Education': ['Curriculum & Instruction', 'Child Development', 'Literacy', 'Classroom Management'],
    'Engineering Science': ['Multidisciplinary Engineering', 'Research', 'Systems Analysis', 'Innovation'],
    'English': ['Literature', 'Creative Writing', 'Rhetoric', 'Linguistics'],
    'Entrepreneurship': ['Startups', 'Innovation', 'Business Strategy', 'Social Entrepreneurship'],
    'Environmental Sciences': ['Climate Change', 'Conservation', 'Ecology', 'Environmental Policy'],
    'Environmental Thought and Practice': ['Sustainability', 'Environmental Justice', 'Policy', 'Community Engagement'],
    'French': ['Language & Culture', 'Literature', 'Translation', 'Francophone Studies'],
    'German': ['Language & Culture', 'Literature', 'Translation', 'German Studies'],
    'Global Culture and Commerce': ['International Business', 'Cultural Studies', 'Global Economics', 'Cross-Cultural Management'],
    'Global Studies': ['International Relations', 'Development', 'Cultural Studies', 'Global Politics'],
    'Global Environments and Sustainability': ['Climate Policy', 'Conservation', 'Sustainable Development', 'Environmental Justice'],
    'Health, Ethics, and Society': ['Bioethics', 'Health Policy', 'Medical Humanities', 'Social Medicine'],
    'Health Sciences Management': ['Healthcare Administration', 'Health Policy', 'Clinical Management', 'Public Health'],
    'History': ['American History', 'European History', 'World History', 'Public History'],
    'History of Art': ['Museum Studies', 'Art Theory', 'Conservation', 'Global Art History'],
    'History of Science and Technology': ['History of Medicine', 'Technology Studies', 'Science & Society', 'Innovation History'],
    'Human Biology': ['Pre-Med', 'Human Physiology', 'Genetics', 'Public Health'],
    'Interdisciplinary Studies': ['Customized Concentration', 'Multiple Disciplines', 'Research Methods', 'Integrated Studies'],
    'Italian': ['Language & Culture', 'Italian Literature', 'Translation', 'Italian Studies'],
    'Japanese Language & Literature': ['Language Acquisition', 'Japanese Literature', 'Translation', 'Japanese Culture'],
    'Jewish Studies': ['Jewish History', 'Hebrew', 'Jewish Philosophy', 'Israeli Studies'],
    'Kinesiology': ['Exercise Science', 'Sports Medicine', 'Biomechanics', 'Coaching'],
    'Korean': ['Language Acquisition', 'Korean Culture', 'Translation', 'Korean Studies'],
    'Latin American Studies': ['History', 'Politics', 'Literature', 'Social Movements'],
    'Leadership': ['Organizational Leadership', 'Social Innovation', 'Management', 'Public Policy'],
    'Linguistics': ['Syntax', 'Semantics', 'Phonology', 'Sociolinguistics'],
    'Materials Science and Engineering': ['Nanomaterials', 'Biomaterials', 'Electronic Materials', 'Structural Materials'],
    'Mathematics': ['Pure Mathematics', 'Applied Mathematics', 'Statistics', 'Actuarial Science'],
    'Mechanical Engineering': ['Thermodynamics', 'Robotics', 'Manufacturing', 'Energy Systems'],
    'Media Studies': ['Digital Media', 'Film & Television', 'Journalism', 'Social Media'],
    'Medieval Studies': ['Medieval History', 'Literature', 'Art & Architecture', 'Philosophy'],
    'Middle Eastern and South Asian Languages and Cultures': ['Language Studies', 'Cultural Studies', 'History', 'Literature'],
    'Music': ['Performance', 'Composition', 'Music Theory', 'Music History'],
    'Neuroscience': ['Cognitive Neuroscience', 'Molecular Neuroscience', 'Behavioral Neuroscience', 'Clinical Neuroscience'],
    'Nursing': ['Clinical Practice', 'Community Health', 'Pediatric Nursing', 'Critical Care'],
    'Philosophy': ['Ethics', 'Logic', 'Metaphysics', 'Political Philosophy'],
    'Physics': ['Astrophysics', 'Quantum Mechanics', 'Condensed Matter', 'Particle Physics'],
    'Political and Social Thought': ['Political Theory', 'Social Philosophy', 'Ethics', 'Critical Theory'],
    'Political Philosophy, Policy, and Law': ['Legal Studies', 'Public Policy', 'Political Theory', 'Constitutional Law'],
    'Politics': ['International Relations', 'Public Administration', 'Political Theory', 'Comparative Politics'],
    'Portuguese': ['Language & Culture', 'Brazilian Studies', 'Translation', 'Lusophone Literature'],
    'Psychology': ['Clinical Psychology', 'Cognitive Psychology', 'Social Psychology', 'Developmental Psychology'],
    'Public Policy and Leadership': ['Policy Analysis', 'Leadership Development', 'Public Administration', 'Social Policy'],
    'Religious Studies': ['Comparative Religion', 'Theology', 'Religion & Society', 'Sacred Texts'],
    'Slavic Languages and Literatures': ['Russian Language', 'Eastern European Literature', 'Cultural Studies', 'Translation'],
    'Sociology': ['Social Inequality', 'Urban Sociology', 'Cultural Sociology', 'Research Methods'],
    'South Asian Languages and Literatures': ['Hindi/Urdu', 'South Asian Literature', 'Cultural Studies', 'Translation'],
    'Spanish': ['Language & Culture', 'Spanish Literature', 'Translation', 'Hispanic Studies'],
    'Special Education': ['Learning Disabilities', 'Behavioral Interventions', 'Inclusive Education', 'Assessment'],
    'Speech Communication Disorders': ['Speech Pathology', 'Audiology', 'Language Development', 'Clinical Practice'],
    'Statistics': ['Data Analysis', 'Statistical Modeling', 'Biostatistics', 'Applied Statistics'],
    'Studio Art': ['Painting', 'Sculpture', 'Photography', 'Digital Art'],
    'Systems Engineering': ['Systems Design', 'Operations Research', 'Project Management', 'Integration'],
    'Urban and Environmental Planning': ['Urban Design', 'Environmental Planning', 'Transportation Planning', 'Community Development'],
    'Women, Gender & Sexuality': ['Feminist Theory', 'Gender Studies', 'LGBTQ+ Studies', 'Intersectionality'],
    'Youth & Social Innovation': ['Youth Development', 'Community Organizing', 'Social Entrepreneurship', 'Education']
  };

  const entryYears = ['2025', '2026', '2027', '2028'];

  const apCreditsOptions = [
    '',
    'AP Research',
    'AP Seminar',
    'AP English Language and Composition',
    'AP English Literature and Composition',
    'AP Spanish Language and Culture',
    'AP Spanish Literature and Culture',
    'AP French Language and Culture',
    'AP German Language and Culture',
    'AP Italian Language and Culture',
    'AP Chinese Language and Culture',
    'AP Japanese Language and Culture',
    'AP Latin',
    'AP Environmental Science',
    'AP Physics 1',
    'AP Physics 2',
    'AP Physics C: Mechanics',
    'AP Physics C: Electricity and Magnetism',
    'AP Chemistry',
    'AP Biology',
    'AP Computer Science Principles',
    'AP Statistics',
    'AP Calculus AB',
    'AP Calculus BC',
    'AP Precalculus',
    'AP Computer Science A',
    'AP World History: Modern',
    'AP European History',
    'AP Human Geography',
    'AP African American Studies',
    'AP US History',
    'AP US Government and Politics',
    'AP Comparative Government and Politics',
    'AP Macroeconomics',
    'AP Microeconomics',
    'AP Psychology',
    'AP 2D Art and Design',
    'AP 3D Art and Design',
    'AP Drawing',
    'AP Art History',
    'AP Music Theory',
  ];

  const handleInputChange = (field: keyof FormData, value: string | string[]) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Clear error when user starts typing
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }

    // Reset focus area when major changes
    if (field === 'major') {
      setFormData(prev => ({
        ...prev,
        focusArea: ''
      }));
    }
  };


  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.major) {
      newErrors.major = 'Please select your intended major';
    }
    if (!formData.focusArea) {
      newErrors.focusArea = 'Please select a focus area';
    }
    if (!formData.entryYear) {
      newErrors.entryYear = 'Please select your entry year';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setSubmitMessage(null);

    try {
      // Store form data in localStorage first
      const dataToStore = {
        ...formData,
        transcript: formData.transcript ? 'uploaded' : null, // Just mark if transcript exists
      };
      localStorage.setItem('pendingUserData', JSON.stringify(dataToStore));

      // Generate the 4-year plan using AI
      setSubmitMessage({
        type: 'success',
        text: 'Generating your personalized 4-year plan...'
      });

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/generate-plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          school: formData.school || 'College of Arts & Sciences',
          major: formData.major,
          focusArea: formData.focusArea,
          entryYear: formData.entryYear,
          apCredits: formData.apCredits,
          additionalDetails: formData.additionalDetails,
          gpa: formData.gpa,
          creditsCompleted: formData.creditsCompleted,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate plan');
      }

      const generatedPlan = await response.json();
      
      // Store the generated plan in localStorage
      localStorage.setItem('generatedPlan', JSON.stringify(generatedPlan));

      setSubmitMessage({
        type: 'success',
        text: '✓ Plan generated! Redirecting...'
      });

      // Redirect to plan page to view the generated plan
      setTimeout(() => {
        router.push('/plan');
      }, 1500);

    } catch (error) {
      console.error('Error generating plan:', error);
      setSubmitMessage({
        type: 'error',
        text: 'Failed to generate plan. Redirecting to dashboard...'
      });

      // Still redirect to dashboard even if plan generation fails
      setTimeout(() => {
        router.push('/dashboard');
      }, 2000);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 to-blue-800 py-8 px-4 flex items-center">
      {/* Tagline Section */}
      <div className="w-1/2 pr-8">
        <h1 className="text-4xl font-bold text-white mb-8">
          {typedTagline}
          {(animationPhase === "typing-tagline") && <span className="animate-blink text-orange-400">|</span>}
        </h1>
        <p className="text-2xl font-semibold text-orange-400">
          {typedSubtitle}{(animationPhase === "typing-subtitle" || animationPhase === "deleting-subtitle") && <span className="animate-blink text-white">|</span>}
        </p>
      </div>

      {/* Form Section */}
      <div className="w-1/2 bg-white rounded-lg shadow-lg p-8 space-y-6">
        <form onSubmit={handleSubmit}>
          {/* School Selection */}
          <Dropdown
            label="Intended School *"
            value={formData.school}
            onChange={(val) => handleInputChange("school", val as string)}
            options={school}
            placeholder="Select your school"
            error={errors.school}
          />

          {/* Major Selection */}
          <Dropdown
            label="Intended Major *"
            value={formData.major}
            onChange={(val) => handleInputChange("major", val as string)}
            options={majors}
            placeholder="Select your major"
            error={errors.major}
          />

          {/* Focus Area Selection */}
            <Dropdown
              label="Focus Area *"
              value={formData.focusArea}
              onChange={(value) => handleInputChange("focusArea", value)}
              placeholder={formData.major ? "Select your focus area" : "Please select a major first"}
              options={formData.major ? focusAreas[formData.major] || [] : []}
              disabled={!formData.major}
              error={errors.focusArea}
            />

          {/* Entry Year Selection */}
          <Dropdown
            label="Entry Year *"
            value={formData.entryYear}
            onChange={(val) => handleInputChange("entryYear", val as string)}
            options={entryYears}
            placeholder="Select your entry year"
            error={errors.entryYear}
          />

          {/* AP/IB Credits */}
          <Dropdown
            label="Advanced Placement (AP/IB) Credits"
            value={formData.apCredits}
            onChange={(val) => handleInputChange("apCredits", val as string[])}
            options={apCreditsOptions.slice(1)}
            multiple
            placeholder="Select AP/IB credits (optional)"
            error={errors.apCredits}
          />


          {/* Transcript Upload for Non-First Years */}
          {formData.entryYear && parseInt(formData.entryYear) < new Date().getFullYear() && (
            <div className="space-y-4 border-t pt-4">
              <h3 className="text-lg font-semibold text-gray-900">For Returning Students</h3>

              <div className='text-gray-700'>
                <label htmlFor="transcript" className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Transcript (Optional)
                </label>
                <input
                  id="transcript"
                  type="file"
                  accept=".pdf"
                  onChange={(e) => {
                    const file = e.target.files?.[0] || null;
                    setFormData(prev => ({ ...prev, transcript: file }));
                  }}
                  className="w-full p-3 border border-gray-300 rounded-lg hover:ring-1 hover:ring-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">Upload your unofficial transcript (PDF only)</p>
              </div>

              <div className='text-gray-700'>
                <label htmlFor="gpa" className="block text-sm font-medium text-gray-700 mb-2">
                  Current GPA (Optional)
                </label>
                <input
                  id="gpa"
                  type="number"
                  step="0.01"
                  min="0"
                  max="4.0"
                  value={formData.gpa}
                  onChange={(e) => setFormData(prev => ({ ...prev, gpa: e.target.value }))}
                  placeholder="3.50"
                  className="w-full p-3 border border-gray-300 rounded-lg hover:ring-1 hover:ring-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                />
              </div>

              <div className='text-gray-700'>
                <label htmlFor="creditsCompleted" className="block text-sm font-medium text-gray-700 mb-2">
                  Credits Completed (Optional)
                </label>
                <input
                  id="creditsCompleted"
                  type="number"
                  min="0"
                  value={formData.creditsCompleted}
                  onChange={(e) => setFormData(prev => ({ ...prev, creditsCompleted: e.target.value }))}
                  placeholder="30"
                  className="w-full p-3 border border-gray-300 rounded-lg hover:ring-1 hover:ring-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                />
              </div>
            </div>
          )}

          {/* Additional Details */}
          <div className='text-gray-700'>
            <label htmlFor="additionalDetails" className="block text-sm font-medium text-gray-700 mb-2">
              Additional Details
            </label>
            <textarea
              id="additionalDetails"
              value={formData.additionalDetails}
              onChange={(e) => handleInputChange('additionalDetails', e.target.value)}
              placeholder="e.g., I want to study abroad in my third year, interested in internships, prefer morning classes..."
              rows={4}
              className="w-full p-3 border border-gray-300 rounded-lg hover:ring-1 hover:ring-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full py-3 px-6 rounded-lg font-medium text-white transition-colors ${
              isLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
            }`}
          >
            {isLoading ? 'Generating Your Plan...' : 'Generate My 4-Year Plan'}
          </button>

          {/* Submit Message */}
          {submitMessage && (
            <div className={`p-4 rounded-lg ${
              submitMessage.type === 'success'
                ? 'bg-green-50 text-green-800 border border-green-200'
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}>
              {submitMessage.text}
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
