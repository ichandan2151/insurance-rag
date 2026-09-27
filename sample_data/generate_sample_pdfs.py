"""Generate sample insurance policy PDFs for testing the RAG pipeline."""
import fitz  # PyMuPDF


POLICIES = {
    "homeowners_policy.pdf": {
        "title": "Standard Homeowners Insurance Policy — HO-3",
        "pages": [
            """HOMEOWNERS INSURANCE POLICY — HO-3 SPECIAL FORM
Policy Number: HO-2024-00147
Effective Date: January 1, 2025 — January 1, 2026

DECLARATIONS PAGE

Named Insured: John A. Smith
Mailing Address: 742 Evergreen Terrace, Springfield, IL 62704

Property Address: Same as above
Policy Period: 12 months beginning January 1, 2025

COVERAGE SUMMARY

Coverage A — Dwelling: $350,000
Coverage B — Other Structures: $35,000 (10% of Coverage A)
Coverage C — Personal Property: $175,000 (50% of Coverage A)
Coverage D — Loss of Use: $105,000 (30% of Coverage A)
Coverage E — Personal Liability: $300,000 per occurrence
Coverage F — Medical Payments to Others: $5,000 per person

Deductible: $1,000 per occurrence (except wind/hail: $2,500)

Annual Premium: $1,847.00""",

            """SECTION I — PROPERTY COVERAGES

COVERAGE A — DWELLING
We cover the dwelling on the residence premises shown in the Declarations, including structures attached to the dwelling and materials and supplies located on or next to the residence premises used to construct, alter, or repair the dwelling or other structures on the residence premises.

This coverage does not apply to land, including land on which the dwelling is located.

COVERAGE B — OTHER STRUCTURES
We cover other structures on the residence premises set apart from the dwelling by clear space. This includes structures connected to the dwelling by only a fence, utility line, or similar connection.

We do not cover other structures:
1. Used in whole or in part for business; or
2. Rented to any person not a tenant of the dwelling, unless used solely as a private garage.

COVERAGE C — PERSONAL PROPERTY
We cover personal property owned or used by an insured while it is anywhere in the world. At your request, we will cover personal property owned by others while the property is on the part of the residence premises occupied by an insured.

Special Limits of Liability: The following limits apply per occurrence:
a. $200 on money, bank notes, bullion, gold, and numismatic property.
b. $1,500 on securities, accounts, deeds, evidences of debt, letters of credit, and manuscripts.
c. $1,500 on watercraft of all types, including trailers and equipment.
d. $1,500 on trailers or semi-trailers not used with watercraft.
e. $2,500 on firearms and related equipment.
f. $2,500 on silverware, goldware, and pewterware.
g. $2,500 on business property on the residence premises.
h. $500 on business property away from the residence premises.""",

            """COVERAGE D — LOSS OF USE
1. Additional Living Expense. If a covered loss makes the residence premises not fit to live in, we cover any necessary increase in living expenses incurred by you so that your household can maintain its normal standard of living. Payment shall be for the shortest time required to repair or replace the damage or, if you permanently relocate, the shortest time required for your household to settle elsewhere.

2. Fair Rental Value. If a covered loss makes that part of the residence premises rented to others or held for rental by you not fit to live in, we cover the fair rental value of such premises less any expenses that do not continue while it is not fit to live in. Payment shall be for the shortest time required to repair or replace such premises.

SECTION I — PERILS INSURED AGAINST (HO-3 SPECIAL FORM)

COVERAGE A — DWELLING and COVERAGE B — OTHER STRUCTURES
We insure against direct physical loss to property described in Coverages A and B, except as excluded under Section I — Exclusions.

COVERAGE C — PERSONAL PROPERTY
We insure against direct physical loss to property described in Coverage C caused by the following perils:
1. Fire or Lightning
2. Windstorm or Hail
3. Explosion
4. Riot or Civil Commotion
5. Aircraft
6. Vehicles
7. Smoke
8. Vandalism or Malicious Mischief
9. Theft
10. Falling Objects
11. Weight of Ice, Snow, or Sleet
12. Accidental Discharge or Overflow of Water or Steam
13. Sudden and Accidental Tearing Apart, Cracking, Burning, or Bulging
14. Freezing
15. Sudden and Accidental Damage from Artificially Generated Electrical Current
16. Volcanic Eruption""",

            """SECTION I — EXCLUSIONS

We do not insure for loss caused directly or indirectly by any of the following:

1. ORDINANCE OR LAW — the enforcement of any ordinance or law regulating the construction, repair, or demolition of a building or other structure.

2. EARTH MOVEMENT — earthquake, volcanic eruption, landslide, mudslide, mudflow, subsidence, sinkhole, or any other earth movement. Direct loss by fire, explosion, theft, or breakage of glass resulting from earth movement is covered.

3. WATER DAMAGE — flood, surface water, waves, tidal water, overflow of a body of water, or spray from any of these. Water or water-borne material which backs up through sewers or drains or which overflows or is discharged from a sump, sump pump, or related equipment is not covered.

4. POWER FAILURE — the failure of power or other utility service if the failure takes place off the residence premises.

5. NEGLECT — neglect of an insured to use all reasonable means to save and preserve property at and after the time of a loss.

6. WAR — war, undeclared war, civil war, insurrection, rebellion, revolution, or warlike act by a military force.

7. NUCLEAR HAZARD — nuclear reaction, radiation, or radioactive contamination.

8. INTENTIONAL LOSS — any loss arising out of any act an insured commits or conspires to commit with the intent to cause a loss.

9. GOVERNMENTAL ACTION — the destruction, confiscation, or seizure of property by order of any governmental or public authority.""",

            """SECTION II — LIABILITY COVERAGES

COVERAGE E — PERSONAL LIABILITY
If a claim is made or a suit is brought against an insured for damages because of bodily injury or property damage caused by an occurrence to which this coverage applies, we will:
1. Pay up to our limit of liability for the damages for which an insured is legally liable; and
2. Provide a defense at our expense by counsel of our choice, even if the suit is groundless, false, or fraudulent.

COVERAGE F — MEDICAL PAYMENTS TO OTHERS
We will pay the necessary medical expenses that are incurred or medically ascertained within three years from the date of an accident causing bodily injury. Medical expenses means reasonable charges for medical, surgical, x-ray, dental, ambulance, hospital, professional nursing, prosthetic devices, and funeral services. This coverage applies only to persons other than an insured.

Coverage F applies to bodily injury:
a. To a person on the insured location with the permission of any insured; or
b. To a person off the insured location, if the bodily injury arises out of a condition on the insured location or the ways immediately adjoining.

SECTION II — EXCLUSIONS
Coverage E and F do not apply to:
1. Expected or intended injury arising out of intentional or criminal acts.
2. Business activities of any insured (with limited exceptions).
3. Professional services rendered by any insured.
4. Any premises owned or rented by any insured which is not an insured location.
5. Motor vehicle liability.
6. Watercraft liability for vessels over 26 feet.
7. Aircraft liability.
8. Communicable disease transmitted by any insured.""",

            """SECTION I — CONDITIONS

1. INSURABLE INTEREST AND LIMIT OF LIABILITY — Even if more than one person has an insurable interest in the property covered, we will not be liable in any one loss for more than the applicable limit of liability.

2. DUTIES AFTER LOSS — In case of a loss to covered property, you must:
a. Give prompt notice to us or our agent;
b. Notify the police in case of loss by theft;
c. Notify the credit card or electronic fund transfer card or access device company in case of loss involving a covered credit card;
d. Protect the property from further damage;
e. Cooperate with us in the investigation of a claim;
f. Prepare an inventory of damaged personal property showing the quantity, description, actual cash value, and amount of loss;
g. Submit to us, within 60 days after requested, a signed, sworn proof of loss.

3. LOSS SETTLEMENT — Covered property losses are settled as follows:
a. Personal property and structures that are not buildings at actual cash value.
b. Buildings under Coverage A or B at replacement cost without deduction for depreciation, subject to the following:
   (1) We will pay the cost to repair or replace with materials of like kind and quality;
   (2) Replacement cost applies only when the property is actually repaired or replaced;
   (3) We will not pay more than the smallest of: the limit of liability, the replacement cost, or the cost to repair.

4. LOSS TO A PAIR OR SET — In case of loss to a pair or set, we may elect to restore or repair any part to restore the pair or set to its value before the loss, or pay the difference between actual cash value before and after the loss.

5. APPRAISAL — If you and we fail to agree on the amount of loss, either may demand an appraisal of the loss. Each party will select a competent appraiser. The appraisers will select an umpire. The appraisers will state separately the actual cash value and the amount of loss. If they fail to agree, they will submit their differences to the umpire.""",
        ],
    },

    "auto_insurance_policy.pdf": {
        "title": "Personal Auto Insurance Policy",
        "pages": [
            """PERSONAL AUTO INSURANCE POLICY
Policy Number: PA-2025-03291
Effective Date: March 1, 2025 — March 1, 2026

DECLARATIONS PAGE

Named Insured: Sarah M. Johnson
Mailing Address: 1234 Oak Avenue, Austin, TX 78701

Vehicle 1: 2023 Toyota Camry SE — VIN: 4T1BF1FK5PU123456
Vehicle 2: 2021 Honda CR-V EX — VIN: 7FARW2H83ME012345

COVERAGE SUMMARY

Part A — Liability Coverage:
  Bodily Injury: $100,000 per person / $300,000 per accident
  Property Damage: $50,000 per accident

Part B — Medical Payments Coverage: $10,000 per person

Part C — Uninsured Motorists Coverage:
  Bodily Injury: $100,000 per person / $300,000 per accident

Part D — Coverage for Damage to Your Auto:
  Collision Deductible: $500
  Other Than Collision (Comprehensive) Deductible: $250

Rental Reimbursement: $50/day, 30-day maximum
Towing and Labor: $100 per disablement

Six-Month Premium: $1,247.00 (Vehicle 1: $623.50, Vehicle 2: $623.50)""",

            """PART A — LIABILITY COVERAGE

INSURING AGREEMENT
We will pay damages for bodily injury or property damage for which any insured becomes legally responsible because of an auto accident. Damages include prejudgment interest awarded against the insured. We will settle or defend, as we consider appropriate, any claim or suit asking for these damages. Our duty to settle or defend ends when our limit of liability for this coverage has been exhausted by payment of judgments or settlements.

WHO IS AN INSURED
1. You or any family member for the ownership, maintenance, or use of any auto or trailer.
2. Any person using your covered auto.
3. For your covered auto, any person or organization but only with respect to legal responsibility for acts or omissions of a person for whom coverage is afforded under this Part.

EXCLUSIONS — Coverage under this Part does not apply to:
1. Any insured who intentionally causes bodily injury or property damage.
2. Property owned or being transported by an insured.
3. Property rented to, used by, or in the care of an insured (except a residence or private garage).
4. Bodily injury to an employee of an insured during the course of employment (workers' compensation applies).
5. Public or livery conveyance (does not apply to a share-the-expense car pool).
6. Vehicles used as a residence or premises.
7. Any vehicle while used in the business of selling, servicing, repairing, parking, or storing vehicles.
8. Using a vehicle without a reasonable belief that the person is entitled to do so.

LIMIT OF LIABILITY
The limit of liability shown in the Declarations for each person for Bodily Injury Liability is our maximum limit of liability for all damages, including damages for care, loss of services, or death, arising out of bodily injury sustained by any one person in any one auto accident. The limit of liability shown in the Declarations for each accident for Bodily Injury Liability is our maximum limit of liability for all damages arising out of bodily injury sustained by two or more persons in any one auto accident.""",

            """PART B — MEDICAL PAYMENTS COVERAGE

INSURING AGREEMENT
We will pay reasonable expenses incurred for necessary medical and funeral services because of bodily injury caused by accident and sustained by an insured. We will pay only those expenses incurred within three years from the date of the accident.

WHO IS AN INSURED
1. You or any family member while occupying, or as a pedestrian when struck by, a motor vehicle designed for use mainly on public roads or a trailer of any type.
2. Any other person while occupying your covered auto.

EXCLUSIONS — Coverage does not apply to bodily injury:
1. Sustained while occupying any motorized vehicle having fewer than four wheels.
2. Sustained while occupying your covered auto when it is being used as a public or livery conveyance.
3. Sustained while occupying any vehicle located for use as a residence or premises.
4. Occurring during the course of employment if workers' compensation benefits are available.
5. Caused by a nuclear weapon, war, or civil disorder.

PART C — UNINSURED MOTORISTS COVERAGE

INSURING AGREEMENT
We will pay compensatory damages which an insured is legally entitled to recover from the owner or operator of an uninsured motor vehicle because of bodily injury sustained by an insured and caused by an accident.

An uninsured motor vehicle means a land motor vehicle or trailer of any type:
1. To which no bodily injury liability bond or policy applies at the time of the accident.
2. To which a liability policy applies but the insurer denies coverage or is insolvent.
3. That is a hit-and-run vehicle whose operator or owner cannot be identified and which hits you or any family member, your covered auto, or a vehicle you or any family member is occupying.

LIMIT OF LIABILITY — The limit of liability shown in the Declarations is our maximum limit of liability for all damages resulting from any one accident, regardless of the number of insureds, claims, or vehicles involved.""",

            """PART D — COVERAGE FOR DAMAGE TO YOUR AUTO

INSURING AGREEMENT
We will pay for direct and accidental loss to your covered auto or any non-owned auto, including their equipment, minus any applicable deductible shown in the Declarations.

If loss is caused by a collision, only that coverage is applicable. If loss results from any covered cause other than collision (comprehensive), only that coverage is applicable.

COLLISION means the upset of your covered auto or a non-owned auto or their impact with another vehicle or object.

OTHER THAN COLLISION (COMPREHENSIVE) losses include:
1. Missiles or falling objects
2. Fire
3. Theft or larceny
4. Explosion or earthquake
5. Windstorm, hail, water, or flood
6. Malicious mischief or vandalism
7. Riot or civil commotion
8. Contact with a bird or animal
9. Breakage of glass

EXCLUSIONS — Coverage does not apply to:
1. Loss to your covered auto which occurs while it is being used as a public or livery conveyance.
2. Damage due and confined to wear and tear, freezing, mechanical or electrical breakdown, or road damage to tires.
3. Loss due to radioactive contamination or war.
4. Loss to equipment designed for the reproduction of sound (unless permanently installed).
5. Loss to tapes, records, discs, or other media.
6. Loss to a camper body or trailer not shown in the Declarations.
7. Loss to any non-owned auto when used by you or any family member without a reasonable belief of being entitled to do so.
8. Loss to any custom furnishings or equipment in or upon any pickup or van (limit: $1,000).

PAYMENT OF LOSS — We may pay for loss in money or repair or replace the damaged or stolen property. We may, at our expense, return any stolen property to you or to the address shown in the Declarations, with payment for any resultant damage.""",

            """GENERAL PROVISIONS

POLICY PERIOD AND TERRITORY
This policy applies only to accidents and losses which occur during the policy period as shown in the Declarations and within the policy territory. The policy territory is the United States, its territories and possessions, Puerto Rico, and Canada. The policy also covers a covered auto while being transported between their ports.

CHANGES
This policy contains all the agreements between you and us. Its terms may not be changed or waived except by endorsement issued by us.

TRANSFER OF YOUR INTEREST IN THIS POLICY
Your rights and duties under this policy may not be assigned without our written consent. However, if a named insured shown in the Declarations dies, coverage will be provided for:
1. The surviving spouse if resident in the same household at the time of death.
2. The legal representative of the deceased person while acting within the scope of the duties of a legal representative.
3. Any person having proper temporary custody of your covered auto until a legal representative is appointed.

CANCELLATION
You may cancel this policy by returning it to us or by notifying us in writing of the date cancellation is to take effect. We may cancel by mailing to the named insured at the address shown at least:
a. 10 days notice if cancellation is for nonpayment of premium; or
b. 20 days notice in all other cases.

After this policy is in effect for 60 days, or if this is a renewal policy, we will not cancel except for:
1. Nonpayment of premium; or
2. License or registration suspension of the named insured or any operator who resides in the same household.

FRAUD — We do not provide coverage for any insured who has made fraudulent statements or engaged in fraudulent conduct in connection with any accident or loss for which coverage is sought under this policy.""",
        ],
    },

    "term_life_policy.pdf": {
        "title": "20-Year Level Term Life Insurance Policy",
        "pages": [
            """LEVEL TERM LIFE INSURANCE POLICY
Policy Number: TL-2024-78503
Effective Date: June 1, 2024

SCHEDULE OF BENEFITS

Policy Owner / Insured: Michael R. Chen
Date of Birth: April 15, 1985
Age at Issue: 39
Risk Class: Preferred Non-Tobacco

Face Amount (Death Benefit): $500,000
Term Period: 20 Years (expires June 1, 2044)
Level Premium Period: 20 Years

Monthly Premium: $42.50
Annual Premium: $495.00

Beneficiary:
  Primary: Emily Chen (spouse) — 100%
  Contingent: David Chen (son) — 50%, Lisa Chen (daughter) — 50%

Conversion Privilege: This policy may be converted to a permanent life insurance policy without evidence of insurability until the insured reaches age 65 or until the end of the term period, whichever comes first.

FREE LOOK PERIOD: You may return this policy within 30 days of delivery for a full refund of premium paid.""",

            """SECTION 1 — DEFINITIONS

"We," "Us," and "Our" refer to Acme Life Insurance Company.
"You" and "Your" refer to the Policy Owner named in the Schedule of Benefits.
"Insured" means the person whose life is insured under this policy.
"Beneficiary" means the person(s) designated to receive the Death Benefit.
"Date of Issue" means the date this policy takes effect as shown in the Schedule of Benefits.
"Policy Anniversary" means the same date each year following the Date of Issue.
"Grace Period" means 31 days following the premium due date.

SECTION 2 — DEATH BENEFIT

We will pay the Face Amount shown in the Schedule of Benefits to the Beneficiary upon receipt of:
1. Due proof of the Insured's death;
2. A completed claim form;
3. A certified copy of the death certificate;
4. This policy, if available.

The Death Benefit will be paid in a single lump sum unless an alternative settlement option has been elected.

ACCELERATED DEATH BENEFIT RIDER (included at no additional cost):
If the Insured is diagnosed with a terminal illness with a life expectancy of 12 months or less, the Policy Owner may request an accelerated payment of up to 75% of the Face Amount. The remaining 25% will be paid to the Beneficiary upon the Insured's death. An administrative fee of $150 will be deducted from the accelerated payment.""",

            """SECTION 3 — PREMIUMS

Premium payments are due on the first day of each month (or annually, if elected). Premiums remain level for the full 20-year term period.

GRACE PERIOD: A grace period of 31 days is granted for the payment of each premium after the first. The policy will remain in force during the grace period. If the Insured dies during the grace period, the unpaid premium will be deducted from the Death Benefit.

REINSTATEMENT: If this policy lapses due to nonpayment of premium, it may be reinstated within 5 years of the date of lapse, subject to:
1. Evidence of insurability satisfactory to us;
2. Payment of all overdue premiums with interest at 6% per annum;
3. Payment of any outstanding policy loans with interest.

SECTION 4 — GENERAL PROVISIONS

ENTIRE CONTRACT: This policy, including the application and any attached riders or endorsements, constitutes the entire contract between the parties.

INCONTESTABILITY: We will not contest this policy after it has been in force during the lifetime of the Insured for two years from the Date of Issue, except for nonpayment of premiums and except for provisions relating to benefits in the event of disability.

MISSTATEMENT OF AGE OR SEX: If the age or sex of the Insured has been misstated, the Death Benefit will be adjusted to the amount that the premium paid would have purchased at the correct age and sex.

SUICIDE EXCLUSION: If the Insured dies by suicide, whether sane or insane, within two years from the Date of Issue, our liability shall be limited to a return of premiums paid, without interest.

ASSIGNMENT: You may assign this policy. We are not responsible for the validity of any assignment. An assignment will not be binding on us until we receive written notice at our home office.""",

            """SECTION 5 — CONVERSION PRIVILEGE

You may convert this policy to a permanent life insurance policy (whole life or universal life) without providing evidence of insurability, subject to the following conditions:

1. Conversion must be requested before the Insured reaches age 65 or before the end of the level term period, whichever is earlier.
2. The face amount of the new policy may not exceed the face amount of this policy.
3. The premium for the new policy will be based on the Insured's attained age at the time of conversion and the current rates for the permanent policy form selected.
4. The new policy will be issued on a standard rate basis regardless of the Insured's current health status.
5. Any riders attached to this policy may not be converted unless specifically stated in the rider.

SECTION 6 — WAIVER OF PREMIUM RIDER

If the Insured becomes totally disabled before age 60 and the disability continues for at least 6 consecutive months, we will waive all premiums that become due during the continuance of such disability.

Total disability means the Insured is unable to perform the material and substantial duties of their own occupation for the first 24 months and unable to perform the duties of any occupation for which they are reasonably suited by education, training, or experience thereafter.

This rider terminates on the Policy Anniversary nearest the Insured's 65th birthday.

Rider Premium: Included in the base premium shown in the Schedule of Benefits.""",
        ],
    },
}


def create_pdf(filename: str, title: str, pages: list[str]):
    """Create a PDF document with the given pages of text."""
    doc = fitz.open()

    for page_text in pages:
        page = doc.new_page(width=612, height=792)  # Letter size
        # Insert text with margins
        rect = fitz.Rect(54, 54, 558, 738)  # 0.75" margins
        page.insert_textbox(
            rect,
            page_text,
            fontsize=9.5,
            fontname="helv",
            align=fitz.TEXT_ALIGN_LEFT,
        )

    doc.save(filename)
    doc.close()
    print(f"  Created: {filename} ({len(pages)} pages)")


if __name__ == "__main__":
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("Generating sample insurance policy PDFs...\n")
    for filename, data in POLICIES.items():
        filepath = os.path.join(script_dir, filename)
        create_pdf(filepath, data["title"], data["pages"])

    print("\nDone! Generated 3 sample insurance policy PDFs.")
