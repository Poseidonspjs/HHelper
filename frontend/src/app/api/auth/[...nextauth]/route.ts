import NextAuth, { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { User } from "next-auth";

// This is a simplified example. In production, you'd validate against a database
const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
        isSignUp: { label: "Is Sign Up", type: "text" }
      },
      async authorize(credentials): Promise<User | null> {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        // TODO: Replace with actual database validation
        // For now, we'll accept any credentials for demo purposes
        // In production, you would:
        // 1. For login: Check if user exists and password matches
        // 2. For signup: Create new user in database

        const user: User = {
          id: credentials.email, // In production, use actual user ID from database
          email: credentials.email,
          name: credentials.email.split('@')[0], // Extract name from email
        };

        return user;
      },
    }),
  ],
  pages: {
    signIn: "/", // Redirect to home page for sign in
  },
  session: {
    strategy: "jwt",
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.email = user.email;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
        session.user.email = token.email as string;
      }
      return session;
    },
  },
  secret: process.env.NEXTAUTH_SECRET || "your-secret-key-change-this-in-production",
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
