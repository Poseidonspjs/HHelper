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

    const formData = await req.formData();
    const file = formData.get("transcript") as File;
    const gpa = formData.get("gpa") as string;
    const creditsCompleted = formData.get("creditsCompleted") as string;

    if (!file) {
      return NextResponse.json(
        { error: "No file provided" },
        { status: 400 }
      );
    }

    // For now, we'll store the file info but you can integrate with Supabase Storage
    // Convert file to base64 or upload to Supabase Storage
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    const base64 = buffer.toString('base64');
    const dataUrl = `data:${file.type};base64,${base64}`;

    // Update user with transcript info
    const updatedUser = await prisma.user.update({
      where: { email: session.user.email },
      data: {
        transcriptUrl: dataUrl, // In production, upload to Supabase Storage and store URL
        gpa: gpa ? parseFloat(gpa) : null,
        creditsCompleted: creditsCompleted ? parseInt(creditsCompleted) : null,
      },
    });

    return NextResponse.json({
      success: true,
      user: updatedUser,
    });
  } catch (error) {
    console.error("Error uploading transcript:", error);
    return NextResponse.json(
      { error: "Failed to upload transcript", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}
