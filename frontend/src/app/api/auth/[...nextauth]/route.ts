import NextAuth, { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { PrismaAdapter } from "@next-auth/prisma-adapter";
import { prisma } from "@/lib/prisma";
import bcrypt from "bcryptjs";
import { User } from "next-auth";

const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
        name: { label: "Name", type: "text" },
        isSignUp: { label: "Is Sign Up", type: "text" }
      },
      async authorize(credentials): Promise<User | null> {
        if (!credentials?.email || !credentials?.password) {
          throw new Error("Email and password are required");
        }

        const isSignUp = credentials.isSignUp === "true";

        if (isSignUp) {
          // Sign up flow
          if (!credentials.name) {
            throw new Error("Name is required for sign up");
          }

          // Check if user already exists
          const existingUser = await prisma.user.findUnique({
            where: { email: credentials.email },
          });

          if (existingUser) {
            throw new Error("User already exists with this email");
          }

          // Hash password
          const hashedPassword = await bcrypt.hash(credentials.password, 10);

          // Create new user (we'll store password in UserProfile for now)
          const user = await prisma.user.create({
            data: {
              email: credentials.email,
              name: credentials.name,
              profile: {
                create: {
                  bio: hashedPassword, // Temporarily storing password hash in bio field
                },
              },
            },
          });

          return {
            id: user.id,
            email: user.email,
            name: user.name || undefined,
          };
        } else {
          // Login flow
          const user = await prisma.user.findUnique({
            where: { email: credentials.email },
            include: { profile: true },
          });

          if (!user || !user.profile) {
            throw new Error("Invalid email or password");
          }

          // Verify password (stored in bio field temporarily)
          const isPasswordValid = await bcrypt.compare(
            credentials.password,
            user.profile.bio || ""
          );

          if (!isPasswordValid) {
            throw new Error("Invalid email or password");
          }

          return {
            id: user.id,
            email: user.email,
            name: user.name || undefined,
          };
        }
      },
    }),
  ],
  pages: {
    signIn: "/",
  },
  session: {
    strategy: "jwt",
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.email = user.email;
        token.name = user.name;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
        session.user.email = token.email as string;
        session.user.name = token.name as string;
      }
      return session;
    },
  },
  secret: process.env.NEXTAUTH_SECRET || "your-secret-key-change-this-in-production",
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
