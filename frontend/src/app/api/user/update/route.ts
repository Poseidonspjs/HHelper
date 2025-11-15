import { NextResponse } from "next/server";
import { getServerSession } from "next-auth/next";
import { prisma } from "@/lib/prisma";

export async function POST(req: Request) {
  try {
    const session = await getServerSession();

    if (!session?.user?.email) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    const body = await req.json();
    const { school, major, focusArea, entryYear, apCredits, additionalDetails } = body;

    // Calculate graduation year (entry year + 4)
    const graduationYear = entryYear ? parseInt(entryYear) + 4 : null;

    // Update user with all form data mapped to correct fields
    const updatedUser = await prisma.user.update({
      where: { email: session.user.email },
      data: {
        school,
        major,
        focusArea,
        entryYear: entryYear ? parseInt(entryYear) : null,
        apCredits: apCredits || [],
        additionalDetails,
        graduationYear,
      },
    });

    return NextResponse.json({
      success: true,
      user: updatedUser,
    });
  } catch (error) {
    console.error("Error updating user:", error);
    return NextResponse.json(
      { error: "Failed to update user data", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}
