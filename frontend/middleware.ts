import { clerkMiddleware } from "@clerk/nextjs/server";

export default clerkMiddleware();

export const config = {
    matcher: [
        // Next.js statik dosyaları hariç her şeyi koruma altına al
        '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
        // API route'ları her zaman çalışsın
        '/(api|trpc)(.*)',
    ],
};