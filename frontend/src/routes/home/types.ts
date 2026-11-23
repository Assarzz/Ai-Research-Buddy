export type CriterionStatus = "old" | "unloaded" | "loading" | "loaded";

export type Criterion = {
	id: number;
	text: string;
	status: CriterionStatus;
	last_updated: string | undefined;
	verdict: string;
	explanation: string;
};

export type PdfFile = {
	id: number;
	file: File;
	criteria: Criterion[];
};

let nextCriterionId = 0;
let nextFileId = 0;

export function newCriterion(text: string): Criterion {
	const id = nextCriterionId;
	nextCriterionId += 1;
	return {
		id,
		text,
		status: "unloaded",
		verdict: "...",
		explanation: "...",
		last_updated: undefined,
	};
}

export function createPdfFile(file: File): PdfFile {
	const id = nextFileId;
	nextFileId += 1;
	return {
		id,
		file,
		criteria: [
			newCriterion("The Paper has an abstract"),
			newCriterion("Each author has their email address included"),
			newCriterion("There is a significance statement"),
		],
	};
}

export function getCriterion(
	id: number,
	criteria: Criterion[],
): Criterion | undefined {
	return criteria.find((c) => c.id === id);
}

export function isSameFile(a: File, b: File): boolean {
	return (
		a === b ||
		(a.name === b.name &&
			a.size === b.size &&
			a.lastModified === b.lastModified)
	);
}
